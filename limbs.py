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

def limbs(array, base):
    for val in array:
        if val >= base:
            raise Exception("limb value must be lte than base")

    return array
