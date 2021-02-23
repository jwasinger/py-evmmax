# subtraction with borrow-out ignored
def limbs_sub(x, y, base) -> [int]:
    assert len(x) == len(y), "num_limbs must be equal"
    num_limbs = len(x)
    res = [0] * num_limbs
    b = 0

    result = limbs_to_num(x, base) - limbs_to_num(y, base)
    return num_to_limbs(abs(result), base, len(x))

    # for i, (x, y) in enumerate(zip(x, y)):
    #     res[i] = abs(x - y - c) % base
    #     c =  abs(x - y - c) // base

    # return c, res

def limbs_addmod(x, y, mod, base) -> [int]:
    carry, result = limbs_add(x, y, base)
    result = result + [carry]

    return limbs_sub(result, mod + [0], base)[:-1]

def limbs_submod(x, y, mod, base) -> [int]:
    # fast version of this would do: 
    #     subtraction first, then adddition, and only use value from first
    #     subtraction if there was no borrow out (x > y)

    result = [0] * len(x)
    if limbs_lte(x, y):
        carry, result = limbs_add(x, y, base)
        result += [carry]

    result = limbs_sub(result, mod + [0], base)[:-1]
    return result

# add two equally-sized multiple-limb number together.
# return a carry/overflow limb and the sum limbs
def limbs_add(x, y, base) -> (int, [int]):
    assert len(x) == len(y), "num_limbs must be equal"

    res = [0] * len(x)

    c = 0
    for i, (x, y) in enumerate(zip(x, y)):
        res[i] = (x + y + c) % base
        c =  (x + y + c) // base

    return c, res

# multiplication of multiple-limb number by a single limb
# return an overflow/carry limb and the product limbs
def limbs_mul_limb(limbs, limb, base) -> (int, [int]):
    res = [0] * len(limbs)
    c = 0

    for i in range(len(limbs)):
        res[i] = (limb * limbs[i] + c) % base
        c = (limb * limbs[i] + c) // base

    return c, res

# given two equally-sized, multiple-limb numbers x, y: return x >= y
def limbs_lte(x, y) -> bool:
    assert len(x) == len(y), "x and y should have same number of limbs"
    
    for (x_limb, y_limb) in reversed(list(zip(x,y))):
        if x_limb < y_limb:
            return True
        elif x_limb > y_limb:
            return False

    return True

# given two equally-sized, multiple-limb numbers x, y: return x >= y
def limbs_gte(x, y) -> bool:
    assert len(x) == len(y), "x and y should have same number of limbs"
    
    for (x_limb, y_limb) in reversed(list(zip(x,y))):
        if x_limb > y_limb:
            return True
        elif x_limb < y_limb:
            return False

    return True

def num_to_limbs(num, base, limb_count=None) -> [int]:
    res = []

    if limb_count != None:
        for _ in range(limb_count):
            res.append(num % base)
            num //= base
    else:
        while num != 0:
            res.append(num % base)
            num //= base

    return res

def limbs_to_num(limbs, base) -> [int]:
    res = 0

    for i, limb in enumerate(limbs):
        res += limb * (base ** i)

    return res

def uint64limbs_from_bytes(b):
    delta = len(b) % 4
    if delta != 0:
        b += [0] * (4 - delta)

    limbs = []

    for i in range(0, len(b), 8):
        limb = b[i]
        for j in range(1, 8):
            limb += b[i + j] * (256 ** j) 
        limbs.append(limb)

    return limbs

def uint64limbs_to_bytes(limbs):
    result = []

    for limb in limbs:
        for _ in range(8):
            result.append(limb & 0xff)
            limb >>= 8

    return result
