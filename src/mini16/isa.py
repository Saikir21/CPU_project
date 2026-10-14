from dataclasses import dataclass
from enum import IntEnum


class Opcode(IntEnum):
    HALT = 0x0
    MOVI = 0x1
    MOV = 0x2
    ADD = 0x3
    SUB = 0x4
    CMP = 0x5
    AND = 0x6
    LOAD = 0x7
    STORE = 0x8
    JMP = 0x9
    JZ = 0xA


# Константы сдвигов, которые задают сетку из 16 бит процессора
OPCODE_SHIFT = 12
OPCODE_MASK = 0xF

RD_SHIFT = 9
RD_MASK = 0x7

RS_SHIFT = 6
RS_MASK = 0x7

IMM9_MASK = 0x1FF
SIGN_BIT_9 = 0x100


@dataclass(slots=True)
class DecodedInstruction:
    opcode: Opcode
    rd: int
    rs: int
    imm: int
    offset: int

# Делаем сдвиги и тд
def decode_instruction(raw_word: int) -> DecodedInstruction:
    raw_word &= 0xFFFF  

    raw_opcode = (raw_word >> OPCODE_SHIFT) & OPCODE_MASK
    opcode = Opcode(raw_opcode)

    rd = (raw_word >> RD_SHIFT) & RD_MASK
    rs = (raw_word >> RS_SHIFT) & RS_MASK

    imm = raw_word & IMM9_MASK

    raw_offset = raw_word & IMM9_MASK
    if raw_offset & SIGN_BIT_9:
        offset = raw_offset - 512
    else:
        offset = raw_offset

    return DecodedInstruction(
        opcode=opcode,
        rd=rd,
        rs=rs,
        imm=imm,
        offset=offset,
    )