from limbs import limbs_mul_limb, limbs_add, limbs_sub, limbs_gte
LIMB_BITS = 64

# montgomery reduction of the product of two multiple-limb numbers
# implementation of HAC 14.36
def mulmodmont(x, y, mod, modinv, base) -> [int]:
    assert len(x) == len(y), "equal sized numbers"

    num_limbs = len(x)
    A = [0] * num_limbs * 2

    for i in range(num_limbs):
        # 2.1) u_i <- ((a_0 + x_i * y_0) * mod_inv ) % b
        ui = ((A[i] + x[i] * y[0] ) * modinv) % base 

        # 2.2) calc A <- (A + x_i * y + u_i * m) / base
        c1, xi_y = limbs_mul_limb(y, x[i], base)
        c2, ui_m = limbs_mul_limb(mod, ui, base)

        c3, A[i:i + num_limbs] = limbs_add(A[i:i + num_limbs], ui_m, base)
        c4, A[i:i + num_limbs] = limbs_add(A[i:i + num_limbs], xi_y, base)

        # for valid inputs, can potentially overflows 2 digits (with overflow in top digit of A[i:i + num_limbs] being 1 at max)
        A[i + num_limbs] = (c1 + c2 + c3 + c4) % base
        if i != num_limbs - 1:
            A[i + num_limbs + 1] = (c1 + c2 + c3 + c4)  // base


        # reduction by b (a shift bsecause b is a power of 2) by discarding lower limb (advancing to the next iteration)

    result = A[-num_limbs:]
    if limbs_gte(result, mod):
        result = limbs_sub(result, mod)
        
    return result

def mulmodmont_noninterleaved(x, y, mod, r, r_inv) -> int:
    m = ((x * y) % r) * modinv
    pass
