from arith import BASE, MAX_LIMB_COUNT, submodx_arith, addmodx_arith, int_to_bigint, bigint_to_int, bigint_gte, mulmont_cios, MontContext
import sys

LIMB_BITS = 64
LIMB_SIZE = 8

def gen_mont_params(mod) -> ([int], int):
    mod_limbs = int_to_bigint(mod)
    modinv = pow(-mod, -1, BASE)

    return (mod_limbs, modinv)

def test_bls12381_mod():
    mod = 0x1a0111ea397fe69a4b1ba7b6434bacd764774b84f38512bf6730d2a0f6b0f6241eabfffeb153ffffb9feffffffffaaab
    pass

def test_montmul_64bit_base():
    test_moduli = {
        "bn128_curve_order": 21888242871839275222246405745257275088696311157297823662689037894645226208583,
        "bls12381_prime_field": 0x1a0111ea397fe69a4b1ba7b6434bacd764774b84f38512bf6730d2a0f6b0f6241eabfffeb153ffffb9feffffffffaaab}
    base = 1 << LIMB_BITS

    for name, modulus in zip(test_moduli.keys(), test_moduli.values()):
        print("    " + name)
        modulus_limbs, modinv = gen_mont_params(modulus)
        r_val = ((1 << LIMB_BITS) ** len(modulus_limbs)) % modulus
        r_squared_val = (r_val ** 2) % modulus
        r_inv_val = pow(r_val, -1, modulus)
        r_squared_limbs = int_to_bigint(r_squared_val, len(modulus_limbs))

        # TODO test with largest, smallest possible values

        test_val = 2
        test_val_limbs = int_to_bigint(test_val, len(modulus_limbs))

        assert bigint_to_int(mulmont_cios(test_val_limbs, r_squared_limbs, modulus_limbs, modinv)) == ( test_val * r_val) % modulus, "should convert normal->montgomery form"

def test_mulmont_cios():
    limb_count = 3
    word_size = 8
    modint = (1 << (word_size * 8 * limb_count)) - 1
    x_int = modint - 1
    y_int = modint - 1
    x = int_to_bigint(x_int, limb_count) 
    y = int_to_bigint(y_int, limb_count) 

    # largest modulus representable with given limb count
    mod = int_to_bigint(modint, limb_count)
    ctx = MontContext()
    ctx.SetMod(mod)

    #modinv = pow(-modint, -1, BASE)
    # TODO setmod

    r_val = ((1 << 64) ** len(mod)) % modint

    res = ctx.MulMont(x, y)
    assert bigint_to_int(res) == (x_int * y_int * r_val) % modint

def gen_inputs(mod: int) -> [(int, int)]:
    yield mod - 1, mod - 1
    yield 2, mod - 1
    yield 0, 0
    yield 1, 1
    yield int(mod / 2), int(mod / 2)

def gen_mulmont_test_suite(limb_count: int) -> [(int, int, int)]:
    # test the max possible modulus/values
    result = []
    max_mod = (1 << (limb_count * LIMB_BITS)) - 1

    for (x,y) in gen_inputs(max_mod):
        yield (x, y, max_mod)

    # test the min possible modulus/values
    if limb_count > 1:
        min_mod = (1 << ((limb_count - 1) * LIMB_BITS)) + 1
        for (x,y) in gen_inputs(min_mod):
            yield (x, y, min_mod)

    # value in the middle of the range
    mid_mod = (1 << ((limb_count * LIMB_BITS) - int(LIMB_BITS / 2))) - 1
    for (x,y) in gen_inputs(mid_mod):
        yield (x, y, mid_mod)

def test_submod():
    print("test_addmod_all_limbs")
    for limb_count in range(1, MAX_LIMB_COUNT + 1):
        test_suite = gen_mulmont_test_suite(limb_count)
        for (x, y, mod) in test_suite:
            x_limbs = int_to_bigint(x, limb_count)
            y_limbs = int_to_bigint(y, limb_count)
            mod_limbs = int_to_bigint(mod, limb_count)

            expected = (x - y) % mod
            res = bigint_to_int(submodx_arith(x_limbs, y_limbs, mod_limbs))
            if expected != res:
                raise Exception("test fail.  not eq expect cond")

def test_addmod():
    for limb_count in range(1, MAX_LIMB_COUNT + 1):
        test_suite = gen_mulmont_test_suite(limb_count)
        for (x, y, mod) in test_suite:
            x_limbs = int_to_bigint(x, limb_count)
            y_limbs = int_to_bigint(y, limb_count)
            mod_limbs = int_to_bigint(mod, limb_count)

            expected = (x + y) % mod
            res = bigint_to_int(addmodx_arith(x_limbs, y_limbs, mod_limbs))
            assert expected == res

def test_mulmont_all_limbs():
    for limb_count in range(1, MAX_LIMB_COUNT + 1):
        test_suite = gen_mulmont_test_suite(limb_count)
        for (x, y, mod) in test_suite:
            x_limbs = int_to_bigint(x, limb_count)
            y_limbs = int_to_bigint(y, limb_count)
            mod_limbs = int_to_bigint(mod, limb_count)

            ctx = MontContext()
            ctx.SetMod(mod_limbs)
            modinv = ctx.mod_inv
            r_inv = pow(1 << (limb_count * LIMB_BITS), -1, mod)

            expected = (x * y * r_inv) % mod
            res = bigint_to_int(mulmont_cios(x_limbs, y_limbs, mod_limbs, modinv))
            assert expected == res

def test_1limb_hardcoded_case1():
    x_limbs = [18446744073709551614]
    y_limbs = [18446744073709551614]
    mod = [18446744073709551615]
    mod_inv = setmod(mod_limbs)

def test_1limb_hardcoded_case2():
    x_limbs = [2]
    y_limbs = [18446744073709551614]
    mod_limbs = [18446744073709551615]
    ctx = MontContext()
    ctx.SetMod(mod_limbs)
    mod_inv = ctx.mod_inv

    res = bigint_to_int(mulmont_cios(x_limbs, y_limbs, mod_limbs, mod_inv))

def test_failure():
    x_limbs = [4]
    y_limbs = [4]
    mod_limbs = [5]
    ctx = MontContext()
    ctx.SetMod(mod_limbs)
    mod_inv = ctx.mod_inv

    res = bigint_to_int(mulmont_cios(x_limbs, y_limbs, mod_limbs, mod_inv))
    sys.exit(0)

#test_failure()

#test_1limb_hardcoded_case2()

print("limbs tests")
#test_mulmont_all_limbs()

#test_limbs()
#test_1limb_hardcoded_case()

print("mulmont test basic")
test_mulmont_cios()

print("montmul test cases on 64bit limbs")
test_montmul_64bit_base()

print("mulmont general tests")
test_mulmont_all_limbs()

print("addmod tests")
test_addmod()

print("submod tests")
test_submod()
