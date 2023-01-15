import math

MAX_LIMB_COUNT = 16
WORD_BITS = 64
BASE = 1 << 64

# -----------------------------------------------------------------------------
#   start of bignum util code and other helpers
#   numbers are expressed as little-endian lists 64bit unsigned integers

# return x - y (omitting borrow-out)
def bigint_sub(x: [int], y: [int]) -> [int]:
    assert len(x) == len(y), "num words must be equal"
    num_words = len(x)
    res = [0] * num_words
    c = 0

    for i in reversed(range(num_words)):
        c, res[i] = sub_with_borrow(x[i], y[i], c)

    return res[:]

# given two equally-sized, multiple-word numbers x, y: return x >= y
def bigint_gte(x, y) -> bool:
    assert len(x) == len(y), "x and y should have same number of words"
    
    for (x_word, y_word) in list(zip(x,y)):
        if x_word > y_word:
            return True
        elif x_word < y_word:
            return False

    return True

# convert an int to a bigint, padding with zero-words if word_count is specified
# and num wouldn't occupy word_count words
def int_to_bigint(num: int, word_count=None) -> [int]:
    res = []

    if word_count != None:
        assert num < (1 << (word_count * WORD_BITS)), "num must be representable with given word_count"
        for _ in range(word_count):
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

    return list(reversed(res))

def bigint_to_int(words: [int]) -> [int]:
    res = 0
    for i, word in enumerate(reversed(words)):
        res += word * (BASE ** i)
    return res

# split a 128bit val into hi/low words
def hi_lo(val128: int) -> (int, int):
    assert val128 < 1 << (WORD_BITS * 2), "val must fit in two words"
    return (val128 >> WORD_BITS) % BASE, val128 % BASE

# single-word subtraction with borrow-in/out
# compute (x - y - b). if negative return (1, abs(x - y - b) % BASE), else return (0, (x - y - b) % BASE)
# b (borrow-in) must be 1 or 0
def sub_with_borrow(x: int, y: int, b: int) -> (int, int):
    assert b == 0 or b == 1, "borrow in must be zero or one"

    res = x - y - b
    b_out = 0
    if res < 0:
        res = BASE - abs(res)
        b_out = 1

    return b_out, res

# CIOS Montgomery multiplication algorithm implementation adapted from section 2.3.2 in https://www.microsoft.com/en-us/research/wp-content/uploads/1998/06/97Acar.pdf
#
# input:
# * x, y, mod - bigint inputs
# * mod_inv - pow(-mod, -1, 1<<SYSTEM_WORD_SIZE_BITS)
# requires:
# * x < mod and y < mod
# * mod % 2 != 0
# returns:
#    (x * y * pow(R, -1, mod)) % mod represented as a bigint
#
def mulmont_cios(x, y, mod, modinv) -> [int]:
    assert len(x) == len(y) and len(y) == len(mod), "{}, {}, {}".format(x, y, mod)
    assert mod[0] != 0, "modulus must occupy all words"

    word_count = len(mod)

    t = [0] * (word_count + 2)

    for i in reversed(range(word_count)):
        # first inner-loop multiply x * y[i]
        c = 0 
        for j in reversed(range(word_count)):
            c, t[j + 2] = hi_lo(t[j + 2] + x[j] * y[i] + c)

        t[0], t[1] = hi_lo(t[1] + c)

        m = (modinv * t[-1]) % BASE
        c, _ = hi_lo(m * mod[-1] + t[-1])

        # second inner-loop: reduction.
        for j in reversed(range(1, word_count)):
            c, t[j + 2] = hi_lo(t[j + 1] + mod[j - 1] * m + c)


        hi, t[2] = hi_lo(t[1] + c)
        t[1] = t[0] + hi

    t = t[1:]
    if t[0] != 0:
        return bigint_sub(t, [0] + mod)[1:]
    elif bigint_gte(t[1:], mod):
        return bigint_sub(t[1:], mod)
    else:
        return t[1:]


# modular addition
# input
#    x, y, mod - bigint inputs
# requires:
#    * x < mod and y < mod
#    * len(x) == len(y) == len(mod)
# returns
#    (x + y) % mod expressed as a bigint
def addmodx_arith(x: [int], y: [int], mod: [int]) -> [int]:
    assert len(x) == len(y) and len(y) == len(mod), "bignum inputs must have same length"
    word_count = len(mod)
    tmp = [0] * word_count
    z = [0] * word_count
    c, c1 = 0, 0

    if bigint_gte(x, mod) or bigint_gte(y, mod):
        raise Exception("x/y must be less than the modulus")

    for i in reversed(range(word_count)):
        c, tmp[i] = hi_lo(x[i] + y[i] + c)

    for i in reversed(range(word_count)):
        c1, z[i] = sub_with_borrow(tmp[i], mod[i], c1)

    if c == 0 and c1 != 0:
        z[:] = tmp[:]

    return z

# modular subtraction
# input
#    x, y, mod - bigint inputs
# requires:
#    * x < mod and y < mod
#    * len(x) == len(y) == len(mod)
# returns
#    (x - y) % mod expressed as a bigint
def submodx_arith(x: [int], y: [int], mod: [int]) -> [int]:
    assert len(x) == len(y) and len(y) == len(mod), "bignum inputs must have same length"
    word_count = len(mod)
    tmp = [0] * word_count
    z = [0] * word_count
    c, c1 = 0, 0

    if bigint_gte(x, mod) or bigint_gte(y, mod):
        raise Exception("x/y must be less than the modulus")

    for i in reversed(range(word_count)):
        c, tmp[i] = sub_with_borrow(x[i], y[i], c)

    for i in reversed(range(word_count)):
        c1, z[i] = hi_lo(tmp[i] + mod[i] + c1)

    if c == 0:
        z[:] = tmp[:]

    return z

class MontContext:
    def __init__(self):
        self.r_squared = None
        self.mod = None

    def SetMod(self, mod: [int]):
        assert len(mod) > 0 and len(mod) <= MAX_LIMB_COUNT, "modulus must be in correct range"
        assert mod[0] % 2 == 1, "modulus must not be even"

        modint = bigint_to_int(mod)
        
        r = 1 << (len(mod) * 64)

        self.mod_inv = pow(-modint, -1, BASE)
        self.r_squared = int_to_bigint(r**2 % modint, len(mod))
        self.mod = mod

    def ToMont(self, val: [int]) -> [int]:
        return mulmont_cios(val, self.r_squared, self.mod, self.mod_inv)

    def ToNorm(self, val: [int]) -> [int]:
        one = [1] + [0] * (len(self.mod) - 1)
        return mulmont_cios(val, one, self.mod, self.mod_inv)

    def MulMont(self, x: [int], y: [int]) -> [int]:
        return mulmont_cios(x, y, self.mod, self.mod_inv)
