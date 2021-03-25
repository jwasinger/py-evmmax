BASE = 10

def madd0(v1, v2):
    assert v1 < BASE and v2 < BASE
    return [(v1 * v2) // BASE, (v1 * v2) % BASE]

def madd1(v1, v2, v3):
    assert v1 < BASE and v2 < BASE and v3 < BASE
    return [(v1 * v2 + v3) // BASE, (v1 * v2 + v3) % BASE]

def madd2(v1, v2, v3, v4):
    assert v1 < BASE and v2 < BASE and v3 < BASE
    return [(v1 * v2 + v3 + v4) // BASE, (v1 * v2 + v3 + v4) % BASE]

def basic_mul(product: [int], x: [int], y: [int]):
    assert len(product) == 4
    assert len(x) == len(y)
    assert len(x) == 2

    c, product[0] = madd0(x[0], y[0])
    c, product[1] = madd1(x[0], y[1], c)
    product[2] = c
    
    c, product[1] = madd1(x[1], y[0], product[1])
    c, product[2] = madd2(x[1], y[1], product[2], c)
    product[3] = c

# 99 * 99 = 9801
p = [0] * 4
basic_mul(p, [9, 9], [9, 9])
assert p == [1, 0, 8, 9]

BASE = 1<<64

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
        basic_mul(product, x, y)
        return 0
    elif limb_count % 2 == 1:
        raise Exception("implement this case")

    x0 = x[:len(x)//2]
    y0 = y[:len(y)//2]
    x1 = x[len(x)//2:]
    y1 = y[len(y)//2:]

    z0 = product[:len(product)//2]
    c = karatsuba_mul_accum(z0, x0, y0, c_in)

    z1 = product[len(product)//4:len(product)//2 + len(product)//4]
    c = karatsuba_mul_accum(z1, x1, y0, c)

    z1 = product[len(product)//4:len(product)//2 + len(product)//4]
    c2 = karatsuba_mul_accum(z1, x0, y1, 0)

    c += c2

    z2 = product[len(product)//2:]
    c = karatsuba_mul_accum(z2, x0, y1, c)

    return c

x = [1, 2, 3, 4]
y = [1, 2, 3, 4]
result = [0] * 8
expected= [1, 4, 0, 1, 7, 6, 8, 1]

c = karatsuba_mul_accum(result, x, y, 0)
import pdb; pdb.set_trace()

assert result == expected
assert c == 0
