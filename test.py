from montmul import mulmodmont
from limbs import num_to_limbs, limbs_to_num, limbs_mul_limb, limbs_add, limbs_sub, limbs_gte

LIMB_BITS = 64

def gen_mont_params(mod, base) -> ([int], int):
    mod_limbs = num_to_limbs(mod, base)
    modinv = pow(-mod, -1, base)

    return (mod_limbs, modinv)

def test_limbs():
    base = 10
    x = [9,9,9]
    assert limbs_mul_limb(x, 2, base) == (1, [8,9,9])

    print("    test num_to_limbs")
    x = 123
    assert num_to_limbs(x, base) == [3, 2, 1]
    assert num_to_limbs(x, base, 4) == [3, 2, 1, 0]

    print("    test limbs_to_num")
    x = [3,2,1]
    y = [3,2,1,0]
    assert limbs_to_num(x, base) == 123
    assert limbs_to_num(y, base) == 123

    print("    test add_limbs")
    x = [9, 9, 9, 0]
    y = [9, 9, 9, 0]
    assert limbs_add(x, y, base) == (0, [8,9,9,1])

    x = [9, 9, 9]
    y = [9, 9, 9]
    assert limbs_add(x, y, base) == (1, [8,9,9])

    print("    test sub_limbs")
    x = [8, 9, 9]
    y = [9, 9, 9]

    # NOTE no borrow out for now
    assert limbs_sub(x, y, base) == [1, 0, 0]
    assert limbs_sub(y, x, base) == [1, 0, 0]
    assert limbs_sub(x, x, base) == [0, 0, 0]

    print("    test limbs_gte")
    assert limbs_gte(x, y) == False
    assert limbs_gte(y, x) == True
    assert limbs_gte(x, x) == True

def test_montmul_hac_testcase():
    base = 10
    m = 72639
    R = 10**5
    x = 5792
    y = 1229
    num_limbs = 5
    modinv = 1 # pow(-m, -1, base)

    m_limbs = num_to_limbs(m, base, num_limbs)
    x_limbs = num_to_limbs(x, base, num_limbs)
    y_limbs = num_to_limbs(y, base, num_limbs)

    assert mulmodmont(x_limbs, y_limbs, m_limbs, modinv, base) == num_to_limbs(39796, base)

def test_montmul_64bit_base():
    test_moduli = {
        "bn128_curve_order": 21888242871839275222246405745257275088696311157297823662689037894645226208583,
        "bls12381_prime_field": 0x1a0111ea397fe69a4b1ba7b6434bacd764774b84f38512bf6730d2a0f6b0f6241eabfffeb153ffffb9feffffffffaaab}
    base = 1 << LIMB_BITS

    for name, modulus in zip(test_moduli.keys(), test_moduli.values()):
        print("    " + name)
        modulus_limbs, modinv = gen_mont_params(modulus, base)
        r_val = ((1 << LIMB_BITS) ** len(modulus_limbs)) % modulus
        r_squared_val = (r_val ** 2) % modulus
        r_inv_val = pow(r_val, -1, modulus)
        r_squared_limbs = num_to_limbs(r_squared_val, base, len(modulus_limbs))

        # TODO test with largest, smallest possible values

        test_val = 2
        test_val_limbs = num_to_limbs(test_val, base, len(modulus_limbs))

        assert limbs_to_num(mulmodmont(test_val_limbs, r_squared_limbs, modulus_limbs, modinv, base), base) == ( test_val * r_val) % modulus, "should convert normal->montgomery form"

print("limbs tests")
test_limbs()

print("montmul test case from hac14.36")
test_montmul_hac_testcase()

print("montmul test cases on 64bit limbs")
test_montmul_64bit_base()

# print("montmul test case with bls12381")
# test_montmul_bls12381()
