EVMMAX_ARITH_OPS = {
    "SETMODMAX": "0c",
    "ADDMODMAX": "0d",
    "SUBMODMAX": "0e",
    "MULMONTMAX": "0f",
}

LIMB_SIZE = 8

SETMOD_OP = "0c"

EVMMAX_ARITH_OPS = {
    "ADDMODMAX": "0d",
    "SUBMODMAX": "0e",
    "MULMONTMAX": "0f",
}

EVM_OPS = {
    "POP": "50",
    "MSTORE": "52",
}

def reverse_endianess(word: str):
    assert len(word) == LIMB_SIZE * 2, "invalid length"

    result = ""
    for i in reversed(range(0, len(word), 2)):
        result += word[i:i+2]
    return result

def calc_limb_count(val: int) -> int:
    assert val > 0, "val must be greater than 0"

    count = 0
    while val != 0:
        val >>= 64
        count += 1
    return count

# split a value into 256bit big-endian words, return them in little-endian format
def int_to_evm_words(val: int, evm384_limb_count: int) -> [str]:
    result = []
    if val == 0:
        return ['00']

    og_val = val
    while val != 0:
        limb = val % (1 << 256)
        val >>= 256

        if limb == 0:
            result.append("00")
            continue

        limb_hex = hex(limb)[2:]
        if len(limb_hex) % 2 != 0:
            limb_hex = "0" + limb_hex

        limb_hex = reverse_endianess(limb_hex)
        if len(limb_hex) < 64:
            limb_hex += (64 - len(limb_hex)) * "0"

        result.append(limb_hex)

    if len(result) * 32 < evm384_limb_count * LIMB_SIZE:
        result = ['00'] * math.ceil((evm384_limb_count * LIMB_SIZE - len(result) * 32) / 32) + result

    return list(reversed(result))

def gen_push_int(val: int) -> str:
    assert val >= 0 and val < (1 << 256), "val must be in acceptable evm word range"

    literal = hex(val)[2:]
    if len(literal) % 2 == 1:
        literal = "0" + literal
    return gen_push_literal(literal)

def gen_push_literal(val: str) -> str:
    assert len(val) <= 64, "val is too big"
    assert len(val) % 2 == 0, "val must be even length"
    push_start = 0x60
    push_op = hex(push_start - 1 + int(len(val) / 2))[2:]

    assert len(push_op) == 2, "bug"

    return push_op + val

def gen_mstore_int(val: int, offset: int) -> str:
    return gen_push_int(val) + gen_push_int(offset) + EVM_OPS["MSTORE"]

def gen_mstore_literal(val: str, offset: int) -> str:
    return gen_push_literal(val) + gen_push_int(offset) + EVM_OPS["MSTORE"]

def reverse_endianess(val: str):
    assert len(val) % 2 == 0, "must have even string"
    result = ""
    for i in reversed(range(0, len(val), 2)):
        result += val[i:i+2]

    return result

class Generator():
    def __self__(self):
        self.bytecode = ""

    def Emit(self, bytecode: str):
        assert len(bytecode) % 2 == 0, "bytecode must be even-lengthed"
        self.bytecode += bytecode
