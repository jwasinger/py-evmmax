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
def karatsuba_mul_accum(product: [int], x: [int], y: [int]):
    assert len(x) == len(y)
    limb_count = len(z1)
    assert len(product) == limb_count * 2

    if limb_count == 1:
        product[0] = (x[0] * y[0]) % BASE
        product[1] = (x[0] * y[0]) // BASE
        return
    elif limb_count % 2 == 1:
        pass # TODO fix this case

    z0 = product[:len(product)//2]
    c, z0[:] = karatsuba_mul_accum(z0, x0, y0, 0)

    z1 = product[len(product)//4:len(product)//2 + len(product)//4]
    c, z1[:] = karatsuba_mul_accum(z1, x1, y0, c)

    z1 = product[len(product)//4:len(product)//2 + len(product)//4]
    c2, z1[:] = karatsuba_mul_accum(z1, x0, y1, 0)

    c += c2

    z2 = product[len(product)//2:]
    c, z2[:] = karatsuba_mul_accum(z2, x0, y1, c)

    if c != 0:
        raise Exception("overflow")
