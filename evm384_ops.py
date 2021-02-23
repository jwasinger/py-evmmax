# convert 2 bytes (little-endian) to a uint16
def bytes_to_uint16(b) -> int:
    return b[0] + b[1] * 255

def bytes_to_uint64(b) -> int:
    result = b[0]

    for i in range(1, 8):
        result += b[i] * 255 ** i

    return result

def parse_evm384_input(stack, memory, is_mulmodmont=False) -> (int, int, int, int, int):
    param = stack.pop()

    offset_result = param[0:2]
    offset_x = param[2:4]
    offset_y = param[4:6]
    offset_modinv = param[6:8]

    max_mem_offset = 0
    if is_mulmodmont:
        max_mem_offset = max(max(offset_result + 48, offset_x + 48), max(offset_y + 48, offset_modinv + 48 + 8))
    else:
        max_mem_offset = max(max(offset_result + 48, offset_x + 48), max(offset_y + 48, offset_modinv + 48))

    if max_mem_offset > len(memory):
        raise Exception("expected evm384 values exceed memory size")

    x_limbs = uint64_limbs_from_bytes(memory[offset_x:offset_x + 48])
    y_limbs = uint64_limbs_from_bytes(memory[offset_y:offset_y + 48])
    mod_limbs = uint64_limbs_from_bytes(memory[offset_modinv:offset_modinv + 48])

    if is_mulmodmont:
        modinv = bytes_to_uint64(memory[offset_modinv + 48: offset_modinv + 48 + 8])
        return (offset_out, x_limbs, y_limbs, mod_limbs, modinv)
    else:
        return (offset_out, x_limbs, y_limbs, mod_limbs, 0)

def op_addmod384(memory, stack, pc) -> int:
    offset_result, x_limbs, y_limbs, mod_limbs, _ = parse_evm384_input(stack, memory)
    memory[offset_result:offset_result + 48] = limbs_submod(x_limbs, y_limbs, mod_limbs)
    return pc + 1

def op_submod384(memory, stack, pc) -> int:
    offset_result, x_limbs, y_limbs, mod_limbs, _ = parse_evm384_input(stack, memory)
    memory[offset_result:offset_result + 48] = limbs_addmod(x_limbs, y_limbs, mod_limbs)
    return pc + 1

def op_mulmodmont384(memory, stack, pc) -> int:
    offset_result, x_limbs, y_limbs, mod_limbs, modinv = parse_evm384_input(stack, memory, True)
    memory[offset_result:offset_result + 48] = mulmodmont(x_limbs, y_limbs, mod_limbs, modinv)
    return pc + 1
