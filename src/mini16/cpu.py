from .isa import DecodedInstruction, Opcode, decode_instruction
from .memory import Memory


class CPU:
    def __init__(self, memory: Memory) -> None:
        self.memory: Memory = memory

        # Регистры, наши 8 значений
        self.registers: list[int] = [0] * 8

        # Специальные регистры
        self.pc: int = 0  # Program Counter

        # Флаги статуса (АЛУ)
        self.flag_z: bool = False  # Zero flag
        self.flag_n: bool = False  # Negative flag

        # Состояние тактового генератора, для входа и выхода
        self.halted: bool = False

    def step(self) -> None:
        # Один такт процессора
        if self.halted:
            return None

        # 1.Выборка
        raw_word = self.memory.read(self.pc)

        self.pc = (self.pc + 1) & 0xFFFF

        # 2.Декодирование
        instr = decode_instruction(raw_word)

        # 3.Исполнение
        self._execute(instr)

    def run(self, max_cycles: int = 10_000) -> None:
        # Непрерывный запуск процессора до команды HALT или лимита тактов
        cycles = 0
        while not self.halted:
            if cycles >= max_cycles:
                raise RuntimeError(
                    f"Превышен лимит выполнения: {max_cycles} циклов (возможно, бесконечный цикл)"
                )
            self.step()
            cycles += 1

    def _update_flags(self, result: int) -> None:
        # Истина, если младшие 16 бит равны 0
        self.flag_z = (result & 0xFFFF) == 0

        # Истина, если число отриц.
        self.flag_n = bool(result & 0x8000)

    def _execute(self, instr: DecodedInstruction) -> None:
        match instr.opcode:
            case Opcode.HALT:
                # Отключение процессора
                self.halted = True

            case Opcode.MOVI:
                # Rd = Imm9
                self.registers[instr.rd] = instr.imm

            case Opcode.MOV:
                # Rd = Rs
                self.registers[instr.rd] = self.registers[instr.rs]

            case Opcode.ADD:
                # Rd = (Rd + Rs) & 0xFFFF
                res = (self.registers[instr.rd] + self.registers[instr.rs]) & 0xFFFF
                self.registers[instr.rd] = res
                self._update_flags(res)

            case Opcode.SUB:
                # Rd = (Rd - Rs) & 0xFFFF
                res = (self.registers[instr.rd] - self.registers[instr.rs]) & 0xFFFF
                self.registers[instr.rd] = res
                self._update_flags(res)

            case Opcode.CMP:
                # Вычисление Rd - Rs ТОЛЬКО для обновления флагов (Rd не меняется)
                res = (self.registers[instr.rd] - self.registers[instr.rs]) & 0xFFFF
                self._update_flags(res)

            case Opcode.AND:
                # Rd = Rd & Rs
                res = self.registers[instr.rd] & self.registers[instr.rs]
                self.registers[instr.rd] = res
                self._update_flags(res)

            case Opcode.LOAD:
                # Rd = Memory[Rs]
                address = self.registers[instr.rs]
                self.registers[instr.rd] = self.memory.read(address)

            case Opcode.STORE:
                # Memory[Rd] = Rs
                address = self.registers[instr.rd]
                value = self.registers[instr.rs]
                self.memory.write(address, value)

            case Opcode.JMP:
                # Относительный переход: PC = PC + Offset
                self.pc = (self.pc + instr.offset) & 0xFFFF

            case Opcode.JZ:
                # Переход по условию Zero: если Z == 1
                if self.flag_z:
                    self.pc = (self.pc + instr.offset) & 0xFFFF