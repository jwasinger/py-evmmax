def gen_mstore_evmmax_elem(dst_slot: int, val: int, limb_count: int) -> str:
    assert dst_slot >= 0 and dst_slot < 11, "invalid dst_slot"

    evm_words = int_to_evm_words(val, limb_count)
    result = ""
    offset = dst_slot * limb_count * LIMB_SIZE
    for word in evm_words:
        result += gen_mstore_literal(word, offset)
        offset += 32

    return result

def gen_encode_evmmax_bytes(*args):
    result = ""
    for b1 in args:
        assert b1 >= 0 and b1 < 256, "argument must be in byte range"

        b1 = hex(b1)[2:]
        if len(b1) == 1:
            b1 = '0'+b1

        result += b1
    return result

def gen_setmod(slot: int, mod: int) -> str:
    limb_count = calc_limb_count(mod)
    result = gen_mstore_evmmax_elem(slot, mod, limb_count)
    result += gen_push_literal(gen_encode_evmmax_bytes(limb_count, slot))
    result += SETMOD_OP
    return result

def gen_addmodmax(*args) -> str:
    return gen_push(gen_encode_evmmax_bytes(args)) + EVMMAX_ARITH_OPS['ADDMODMAX']

def gen_submodmax(*args) -> str:
    return gen_push(gen_encode_evmmax_bytes(args)) + EVMMAX_ARITH_OPS['SUBMODMAX']

def gen_mulmontmax(*args) -> str:
    return gen_push(gen_encode_evmmax_bytes(args)) + EVMMAX_ARITH_OPS['MULMONTMAX']
