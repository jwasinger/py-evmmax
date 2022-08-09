from arith import int_to_limbs, limbs_to_int, limbs_gte, mulmont_cios

LIMB_BITS = 64

def gen_mont_params(mod, base) -> ([int], int):
    mod_limbs = int_to_limbs(mod, base)
    modinv = pow(-mod, -1, base)

    return (mod_limbs, modinv)

def test_limbs():
    base = 10
    x = [9,9,9]

    print("    test int_to_limbs")
    x = 123
    assert int_to_limbs(x, base) == [3, 2, 1]
    assert int_to_limbs(x, base, 4) == [3, 2, 1, 0]

    print("    test limbs_to_int")
    x = [3,2,1]
    y = [3,2,1,0]
    assert limbs_to_int(x, base) == 123
    assert limbs_to_int(y, base) == 123
    x += [0]
    z = [4,2,1,0]

    print("    test limbs_gte")
    assert limbs_gte(x, y) == True
    assert limbs_gte(y, x) == True
    assert limbs_gte(x, x) == True
    assert limbs_gte(z, x) == True
    assert limbs_gte(x, z) == False

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
        r_squared_limbs = int_to_limbs(r_squared_val, base, len(modulus_limbs))

        # TODO test with largest, smallest possible values

        test_val = 2
        test_val_limbs = int_to_limbs(test_val, base, len(modulus_limbs))

        assert limbs_to_int(mulmont_cios(test_val_limbs, r_squared_limbs, modulus_limbs, modinv, 8), base) == ( test_val * r_val) % modulus, "should convert normal->montgomery form"

def test_mulmont_cios():
    limb_count = 3
    word_size = 8
    word_mod = 1 << (word_size * 8)
    modint = (1 << (word_size * 8 * limb_count)) - 1
    x_int = modint - 1
    y_int = modint - 1
    x = int_to_limbs(x_int, word_mod, limb_count) 
    y = int_to_limbs(y_int, word_mod, limb_count) 

    # largest modulus representable with given limb count
    mod = int_to_limbs(modint, word_mod, limb_count)
    modinv = pow(-modint, -1, word_mod)

    r_val = ((1 << 64) ** len(mod)) % modint

    res = mulmont_cios(x, y, mod, modinv, word_size)
    res = res[:-1]
    assert limbs_to_int(res, 1<<64) == (x_int * y_int * r_val) % modint

def test_mulmont_all_limbs():
    pass


print("limbs tests")
test_limbs()

print("mulmont test basic")
test_mulmont_cios()

print("montmul test cases on 64bit limbs")
test_montmul_64bit_base()

print("mulmont general tests")
test_mulmont_all_limbs()
