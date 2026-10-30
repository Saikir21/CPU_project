import pytest
from src.mini16 import Assembler, Opcode, decode_instruction


def test_assemble_basic_instructions():
    asm = Assembler()
    code = """
        MOVI R0, 10
        MOVI R1, 25
        ADD  R0, R1
        HALT
    """
    binary = asm.assemble(code)

    # Проверка совпадения с ранее рассчитанными вручную словами
    assert binary == [0x100A, 0x1219, 0x3040, 0x0000]


def test_assemble_labels_and_relative_jumps():
    asm = Assembler()
    code = """
    start:
        ADD R0, R1
        JZ  end
        JMP start
    end:
        HALT
    """
    binary = asm.assemble(code)

    # Проверяем декодером правильность вычисленных смещений
    # Инструкция 0 (addr 0): ADD R0, R1
    # Инструкция 1 (addr 1): JZ end (end на адресе 3 -> offset = 3 - (1 + 1) = +1)
    # Инструкция 2 (addr 2): JMP start (start на адресе 0 -> offset = 0 - (2 + 1) = -3)
    # Инструкция 3 (addr 3): HALT

    jz_decoded = decode_instruction(binary[1])
    assert jz_decoded.opcode == Opcode.JZ
    assert jz_decoded.offset == 1

    jmp_decoded = decode_instruction(binary[2])
    assert jmp_decoded.opcode == Opcode.JMP
    assert jmp_decoded.offset == -3