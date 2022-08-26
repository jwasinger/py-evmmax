import math

MAX_LIMB_COUNT = 12
LIMB_BITS = 64
WORD_SIZE = 8
LIMB_SIZE = 8
BASE = 1 << 64

# -----------------------------------------------------------------------------
#   start of bignum util code and other helpers
#   numbers are expressed as little-endian lists 64bit unsigned integers

# return x - y (omitting borrow-out)
def limbs_sub(x: [int], y: [int]) -> [int]:
    assert len(x) == len(y), "num_limbs must be equal"
    num_limbs = len(x)
    res = [0] * num_limbs
    c = 0

    for i in range(num_limbs):
        c, res[i] = sub_with_borrow(x[i], y[i], c)

    return res[:]

# given two equally-sized, multiple-limb numbers x, y: return x >= y
def limbs_gte(x, y) -> bool:
    assert len(x) == len(y), "x and y should have same number of limbs"
    
    for (x_limb, y_limb) in reversed(list(zip(x,y))):
        if x_limb > y_limb:
            return True
        elif x_limb < y_limb:
            return False

    return True

# convert an int to a bigint, padding with zero-limbs if limb_count is specified
# and num wouldn't occupy limb_count limbs
def int_to_limbs(num: int, limb_count=None) -> [int]:
    res = []

    if limb_count != None:
        assert num < (1 << (limb_count * LIMB_BITS)), "num must be representable with given limb_count"
        for _ in range(limb_count):
            res.append(num % BASE)
            num //= BASE
    else:
        if num == 0:
            return [0]

        while num != 0:
            if num < BASE:
                res.append(num)
                break

            res.append(num % BASE)
            num //= BASE

    return res

def limbs_to_int(limbs: [int]) -> [int]:
    res = 0
    for i, limb in enumerate(limbs):
        res += limb * (BASE ** i)
    return res

# split a 128bit val into hi/low words
def hi_lo(val128: int) -> (int, int):
    assert val128 < 1 << (LIMB_BITS * 2), "val must fit in two words"
    return (val128 >> LIMB_BITS) % BASE, val128 % BASE

# compute (x - y - b). if negative 1, (x - y - b) % BASE, else return 0, (x - y - b) % BASE
# b (borrow-in) must be 1 or 0
def sub_with_borrow(x: int, y: int, b: int) -> (int, int):
    assert b == 0 or b == 1, "borrow in must be zero or one"

    res = x - y - b
    b_out = 0
    if res < 0:
        res = BASE - abs(res)
        b_out = 1

    return b_out, res

# -----------------------------------------------------------------------------
# start of EVMMAX arithmetic

# implementation adapted from section 2.3.2 in https://www.microsoft.com/en-us/research/wp-content/uploads/1998/06/97Acar.pdf
# mulmont_cios computes (x * y * pow(R, -1, mod)) % mod, where R = 1 << (limb_count * word_size * 8)
# modinv must be pow(-mod, -1, BASE)
def mulmont_cios(x, y, mod, modinv) -> [int]:
    assert len(x) == len(y) and len(y) == len(mod), "{}, {}, {}".format(x, y, mod)
    assert mod[-1] != 0, "modulus must occupy all limbs"

    limb_count = len(mod)

    t = [0] * (limb_count + 2)

    for i in range(limb_count):
        # first inner-loop multiply x * y[i]
        c = 0 
        for j in range(limb_count):
            c, t[j] = hi_lo(t[j] + x[j] * y[i] + c)

        t[limb_count + 1], t[limb_count] = hi_lo(t[limb_count] + c)

        m = (modinv * t[0]) % BASE
        c, _ = hi_lo(m * mod[0] + t[0])

        # second inner-loop: reduction.
        for j in range(1, limb_count):
            c, t[j - 1] = hi_lo(t[j] + mod[j] * m + c)

        hi, t[limb_count - 1] = hi_lo(t[limb_count] + c)
        t[limb_count] = t[limb_count + 1] + hi

    t = t[:-1]
    if t[-1] != 0:
        return limbs_sub(t, mod + [0])[:-1]
    elif limbs_gte(t[:-1], mod):
        return limbs_sub(t[:-1], mod)
    else:
        return t[:-1]


# addmod computes (x + y) % mod
def addmod(x: [int], y: [int], mod: [int]) -> [int]:
    assert len(x) == len(y) and len(y) == len(mod), "bignum inputs must have same length"
    limb_count = len(mod)
    tmp = [0] * limb_count
    z = [0] * limb_count
    c, c1 = 0, 0

    if limbs_gte(x, mod) or limbs_gte(y, mod):
        raise Exception("x/y must be less than the modulus")

    for i in range(limb_count):
        c, tmp[i] = hi_lo(x[i] + y[i] + c)

    for i in range(limb_count):
        c1, z[i] = sub_with_borrow(tmp[i], mod[i], c1)

    if c == 0 and c1 != 0:
        z[:] = tmp[:]

    return z

# submod computes (x - y) % mod
def submod(x: [int], y: [int], mod: [int]) -> [int]:
    assert len(x) == len(y) and len(y) == len(mod), "bignum inputs must have same length"
    limb_count = len(mod)
    tmp = [0] * limb_count
    z = [0] * limb_count
    c, c1 = 0, 0

    if limbs_gte(x, mod) or limbs_gte(y, mod):
        raise Exception("x/y must be less than the modulus")

    for i in range(limb_count):
        c, tmp[i] = sub_with_borrow(x[i], y[i], c)

    for i in range(limb_count):
        c1, z[i] = hi_lo(tmp[i] + mod[i] + c1)

    if c == 0:
        z[:] = tmp[:]

    return z

class MontContext:
    def __init__(self):
        self.r_squared = None
        self.mod = None
        self.r_inv = None
        pass

    def SetMod(self, mod: [int]):
        assert len(mod) > 0 and len(mod) <= MAX_LIMB_COUNT, "modulus must be in correct range"
        assert mod[0] % 2 == 1, "modulus must not be even"

        modint = limbs_to_int(mod)
        
        r = 1 << (len(mod) * 64)

        self.mod_inv = pow(-modint, -1, BASE)
        self.r_squared = int_to_limbs(r**2 % modint)
        self.mod = mod

    def ToMont(self, val: [int]) -> [int]:
        return mulmont_cios(val, self.r_squared, self.mod, self.mod_inv)

    def ToNorm(self, val: [int]) -> [int]:
        return mulmont_cios(val, 1, self.mod, self.mod_inv)

    def MulMont(self, x: [int], y: [int]) -> [int]:
        return mulmont_cios(x, y, self.mod, self.mod_inv)
