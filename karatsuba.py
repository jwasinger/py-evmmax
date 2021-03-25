
def karatsuba_mul(product: [int], x: [int], y: [int]):
    assert len(z1) == len(z2) and len(z1) == len(z0)
    assert len(product) == len(z2) * 2

    pass

def karatsuba_add(product: [int], z2: [int], z1: [int], z0: [int]):
    assert len(z1) == len(z2) and len(z1) == len(z0)
    assert len(product) == len(z2) * 2

    c = limbs_add(product[0:len(product)//2], product[0:len(product)//2], z0)
    product[len(product)//2] += c

    c, limbs_add(product[len(product)//4:len(product)//2], product[len(product)//4:len(product)//2], z1)
    product[len(product)//2 + len(product)//4] += c

    # carry out shouldn't be possible here
    c, limbs_add(product[len(product)//2:len(product)//2 + len(product)//4], product[len(product)//2:len(product)//4], z2)
    if c != 0:
        raise Exception("overflow")

def karatsuba(x: [int], y: [int], context: ArithContext) -> [int]:

# z2 = x1 * y1
# z1 = x1 * y0 + x0 * y1
# z0 = x0 * y0

# final result is
# | -- z2 -- |
# +
#       | -- z1 -- | 
# +
#             | -- z0 -- |
# | -- || -- || -- | --  | <- word sizes
