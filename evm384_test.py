from evm384_ops import op_mulmodmont384, op_submod384, op_addmod384

def encode_uint16_le(num):
    return [num & 0xff, num >> 8]

def test_mulmodmont384():
    zero = 0
    x = 2
    one = 1
    mod = 4002409555221667393417789825735904156556882819939007885332058136124031650490837864442687629129015664037894272559787
    modinv = pow(-mod, -1, (1<<64))

    zero_bytes = zero.to_bytes(48, 'little')
    x_bytes = x.to_bytes(48, 'little')
    one_bytes = one.to_bytes(48, 'little')
    mod_bytes = mod.to_bytes(48, 'little')
    modinv_bytes = modinv.to_bytes(8, 'little')

    memory = list(zero_bytes) + list(x_bytes) + list(one_bytes) + list(mod_bytes) + list(modinv_bytes)
    result_offset = 0
    x_offset = 48
    y_offset = 96
    mod_offset = 144
    stack_param = encode_uint16_le(result_offset) + encode_uint16_le(x_offset) + encode_uint16_le(y_offset) + encode_uint16_le(mod_offset)  + ([0] * 24)
    stack = [stack_param]

    op_mulmodmont384(memory, stack, 0)

def test_addmod384():
    pass

def test_submod384():
    pass

test_mulmodmont384()
