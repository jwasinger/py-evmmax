import math

MAX_LIMB_COUNT = 12
LIMB_BITS = 64
WORD_SIZE = 8
LIMB_SIZE = 8
BASE = 1 << 64

# -----------------------------------------------------------------------------
#   start of `limbs` bignum utility code
#   express numbers as little-endian lists of values of base `base`

def limbs_sub(x: [int], y: [int], base: int) -> (int, [int]):
    assert len(x) == len(y), "num_limbs must be equal"
    num_limbs = len(x)
    res = [0] * num_limbs
    c = 0

    for i in range(num_limbs):
        c, res[i] = sub_with_borrow(x[i], y[i], c, LIMB_SIZE)

    #result = limbs_to_int(x, base) - limbs_to_int(y, base)
    return res[:]#int_to_limbs(abs(result), base, len(x))

# given two equally-sized, multiple-limb numbers x, y: return x >= y
def limbs_gte(x, y) -> bool:
    assert len(x) == len(y), "x and y should have same number of limbs"
    
    for (x_limb, y_limb) in reversed(list(zip(x,y))):
        if x_limb > y_limb:
            return True
        elif x_limb < y_limb:
            return False

    return True

# TODO assert that the number can actually be represented by `limb_count` limbs
def int_to_limbs(num, base, limb_count=None) -> [int]:
    res = []

    if limb_count != None:
        for _ in range(limb_count):
            res.append(num % base)
            num //= base
    else:
        if num == 0:
            return [0]

        while num != 0:
            if num < base:
                res.append(num)
                break

            res.append(num % base)
            num //= base

    return res

def limbs_to_int(limbs: [int], base: int) -> [int]:
    res = 0

    for i, limb in enumerate(limbs):
        res += limb * (base ** i)

    return res


def hi_lo(double_word: int, word_size: int) -> (int, int):
    assert double_word < (1<<(word_size * 8 * 2)), "val must fit in two words"
    base = 1 << (word_size * 8)
    return (double_word >> (word_size * 8)) % base, double_word % base

# -----------------------------------------------------------------------------
# start of arithmetic

# implementation adapted from section 2.3.2 in https://www.microsoft.com/en-us/research/wp-content/uploads/1998/06/97Acar.pdf
# mulmont_cios computes (x * y * pow(R, -1, mod)) % mod, where R = 1 << (limb_count * word_size * 8)
# modinv must be pow(-mod, -1, 1 << (word_size * 8))
def mulmont_cios(x, y, mod, modinv, word_size) -> [int]:
    assert len(x) == len(y) and len(y) == len(mod), "{}, {}, {}".format(x, y, mod)
    assert mod[-1] != 0, "modulus must occupy all limbs"

    limb_count = len(mod)

    t = [0] * (limb_count + 2)

    for i in range(limb_count):
        # first inner-loop multiply x * y[i]
        c = 0 
        for j in range(limb_count):
            c, t[j] = hi_lo(t[j] + x[j] * y[i] + c, word_size)

        t[limb_count + 1], t[limb_count] = hi_lo(t[limb_count] + c, word_size)

        m = (modinv * t[0]) % (1 << (word_size * 8)) 
        c, _ = hi_lo(m * mod[0] + t[0], word_size)

        # second inner-loop: reduction.
        for j in range(1, limb_count):
            c, t[j - 1] = hi_lo(t[j] + mod[j] * m + c, word_size)

        hi, t[limb_count - 1] = hi_lo(t[limb_count] + c, word_size)
        t[limb_count] = t[limb_count + 1] + hi

    t = t[:-1]
    if t[-1] != 0:
        return limbs_sub(t, mod + [0], 1<<64)[:-1]
    elif limbs_gte(t[:-1], mod):
        return limbs_sub(t[:-1], mod, 1<<64)
    else:
        return t[:-1]

def sub_with_borrow(x: int, y: int, b: int, word_size: int) -> (int, int):
    assert b == 0 or b == 1, "borrow in must be zero or one"

    res = x - y - b
    b_out = 0
    if res < 0:
        res = BASE - abs(res)
        b_out = 1

    return b_out, res

# addmod computes (x + y) % mod
def addmod(x: [int], y: [int], mod: [int], word_size: int) -> [int]:
    assert len(x) == len(y) and len(y) == len(mod), "bignum inputs must have same length"
    limb_count = len(mod)
    tmp = [0] * limb_count
    z = [0] * limb_count
    c, c1 = 0, 0

    if limbs_gte(x, mod) or limbs_gte(y, mod):
        raise Exception("x/y must be less than the modulus")

    for i in range(limb_count):
        c, tmp[i] = hi_lo(x[i] + y[i] + c, LIMB_SIZE)

    for i in range(limb_count):
        c1, z[i] = sub_with_borrow(tmp[i], mod[i], c1, LIMB_SIZE)

    if c == 0 and c1 != 0:
        z[:] = tmp[:]

    return z

# submod computes (x - y) % mod
def submod(x: [int], y: [int], mod: [int], word_size: int) -> [int]:
    assert len(x) == len(y) and len(y) == len(mod), "bignum inputs must have same length"
    limb_count = len(mod)
    tmp = [0] * limb_count
    z = [0] * limb_count
    c, c1 = 0, 0

    if limbs_gte(x, mod) or limbs_gte(y, mod):
        raise Exception("x/y must be less than the modulus")

    for i in range(limb_count):
        c, tmp[i] = sub_with_borrow(x[i], y[i], c, LIMB_SIZE)

    for i in range(limb_count):
        c1, z[i] = hi_lo(tmp[i] + mod[i] + c1, LIMB_SIZE)

    if c == 0:
        z[:] = tmp[:]

    return z

# setmod computes a modulus-specific constant used by the CIOS algorithm (and also some other algorithms that operate at small bit-widths)
def setmod(mod: [int], word_size: int) -> int:
    assert len(mod) > 0 and len(mod) <= MAX_LIMB_COUNT, "modulus must be in correct range"
    result = None
    try:
        result = pow(-limbs_to_int(mod, BASE), -1, 1 << (word_size * 8))
    except Exception as e:
        import pdb; pdb.set_trace()

    return result
    
# -----------------------------------------------------------------------------
# start of test cases

def gen_max_mod(limb_count: int, word_size: int) -> int:
    return (1 << (limb_count * word_size * 8)) - 1

def gen_mid_mod(limb_count: int, word_size: int) -> int:
    return (1 << ((limb_count * word_size * 8) - (word_size * 4))) - 1

def gen_min_mod(limb_count: int, word_size: int) -> int:
    return (1 << ((limb_count - 1) * word_size)) - 1

#for limb_count in range(1, MAX_LIMB_COUNT):
#    print(limb_count)
#    # test that mulmont_cios(mod - 1, mod - 1, max_mod, modinv) == (mod - 1) * (mod - 1) * pow(1 << (limb_count * LIMB_BITS), -1, mod)
#    #max_mod = (1 << (limb_count * 64)) - 1
#    max_mod = gen_mid_mod(limb_count, 8)
#    modinv = setmod(int_to_limbs(max_mod, BASE), WORD_SIZE)
#    
#    x = int_to_limbs(max_mod - 1, BASE, limb_count=limb_count)
#    y = int_to_limbs(max_mod - 1, BASE, limb_count=limb_count)
#    assert limbs_to_int(mulmont_cios(x, y, int_to_limbs(max_mod, BASE), modinv, WORD_SIZE), BASE) == ((max_mod - 1) * (max_mod - 1) * pow(1 << (limb_count * LIMB_BITS), -1, max_mod)) % max_mod
