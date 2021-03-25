import numpy
from limbs import limbs_add

BASE = 10

def madd(v1, v2):
    assert v1 < BASE and v2 < BASE
    return [(v1 * v2) // BASE, (v1 * v2) % BASE]

def madd1(v1, v2, v3):
    assert v1 < BASE and v2 < BASE and v3 < BASE
    return [(v1 * v2 + v3) // BASE, (v1 * v2 + v3) % BASE]

def madd2(v1, v2, v3, v4):
    assert v1 < BASE and v2 < BASE and v3 < BASE
    return [(v1 * v2 + v3 + v4) // BASE, (v1 * v2 + v3 + v4) % BASE]

def basic_schoolbook_mul(product: [int], x: [int], y: [int]):
    assert len(product) == 4
    assert len(x) == len(y)
    assert len(x) == 2

    c, product[0] = madd(x[0], y[0])
    c, product[1] = madd1(x[0], y[1], c)
    product[2] = c
    
    c, product[1] = madd1(x[1], y[0], product[1])
    c, product[2] = madd2(x[1], y[1], product[2], c)
    product[3] = c

# 99 * 99 = 9801
p = [0] * 4
basic_schoolbook_mul(p, [9, 9], [9, 9])
assert p == [1, 0, 8, 9]

# product <- product + x * y + c_in
# returns carry out
def basic_mul_accum(product: [int], x: int, y: int, c_in) -> int:
    hi, lo = madd1(x, y, c_in)
    c_out, product[0:2] = limbs_add(product[0:2], [lo, hi], BASE)
    return c_out

def karatsuba_basic_step_accum(product: [int], x: [int], y: [int], c_in) -> int:
    assert len(product) == 4 and len(x) == 2 and len(y) == 2
    c_out = basic_mul_accum(product[0:2], x[1], y[1], c_in=0)

    c_out = basic_mul_accum(product[1:3], x[1], y[0], c_in=c_out)
    c_out_2 = basic_mul_accum(product[1:3], x[1], y[0], c_in=0)

    # TODO check that this carry addition can't overflow
    c_out = c_out + c_out_2

    return basic_mul_accum(product[2:4], x[0], y[0], c_in=c_out)

# multiplication step:
#
# z2 = x1 * y1
# z1 = x1 * y0 + x0 * y1
# z0 = x0 * y0
#
# addition step:
#
# | -- z2 -- |
# +
#       | -- z1 -- | 
# +
#             | -- z0 -- |
# | -- || -- || -- | --  |
# | ----- product ------ |
# highest           lowest
def karatsuba_mul_accum(product: [int], x: [int], y: [int], c_in) -> int:
    assert len(x) == len(y)
    limb_count = len(x)
    assert len(product) == limb_count * 2

    if limb_count == 1:
        return basic_mul_accum(product, x[0], y[0], c_in)
    elif limb_count == 2:
        return karatsuba_basic_step_accum(product, x, y, c_in)
    elif limb_count % 2 == 1:
        raise Exception("implement this case")

    x0 = x[:len(x)//2]
    y0 = y[:len(y)//2]
    x1 = x[len(x)//2:]
    y1 = y[len(y)//2:]

    z0 = product[:len(product)//2]
    c = karatsuba_mul_accum(z0, x0, y0, c_in=c_in)

    z1 = product[len(product)//4:len(product)//2 + len(product)//4]
    c = karatsuba_mul_accum(z1, x1, y0, c_in=c)

    z1 = product[len(product)//4:len(product)//2 + len(product)//4]
    c2 = karatsuba_mul_accum(z1, x0, y1, c_in=0)

    # TODO the carry can't overflow here right?
    c += c2

    z2 = product[len(product)//2:]
    c = karatsuba_mul_accum(z2, x0, y1, c)

    return c

x = numpy.array([1, 2, 3, 4])
y = numpy.array([1, 2, 3, 4])
result = numpy.array([0] * 8)
expected= numpy.array([1, 4, 0, 1, 7, 6, 8, 1])

c = karatsuba_mul_accum(result, x, y, 0)
import pdb; pdb.set_trace()

assert result == expected
assert c == 0
