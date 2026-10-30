import re
from .isa import Opcode

# Таблица соответствия мнемоник опкодам
MNEMONICS: dict[str, Opcode] = {
    "HALT": Opcode.HALT,
    "MOVI": Opcode.MOVI,
    "MOV": Opcode.MOV,
    "ADD": Opcode.ADD,
    "SUB": Opcode.SUB,
    "CMP": Opcode.CMP,
    "AND": Opcode.AND,
    "LOAD": Opcode.LOAD,
    "STORE": Opcode.STORE,
    "JMP": Opcode.JMP,
    "JZ": Opcode.JZ,
}


class Assembler:
    def __init__(self) -> None:
        self.labels: dict[str, int] = {}

    def _parse_register(self, reg_str: str) -> int:
        """Преобразует строку вида 'R0'-'R7' в число 0-7."""
        reg_str = reg_str.strip().upper()
        if not re.fullmatch(r"R[0-7]", reg_str):
            raise ValueError(
                f"Некорректное имя регистра: {reg_str}. Ожидается R0-R7."
            )
        return int(reg_str[1])

    def _parse_immediate(self, imm_str: str) -> int:
        """Преобразует строковое число (десятичное или hex) в int."""
        imm_str = imm_str.strip()
        if imm_str.startswith(("0x", "0X")):
            return int(imm_str, 16)
        return int(imm_str, 10)

    def assemble(self, source_code: str) -> list[int]:
        """Компилирует исходный ассемблерный текст в список 16-битных машинных слов."""
        self.labels.clear()
        raw_lines = source_code.splitlines()

        # Очистка от комментариев и пустых строк
        clean_lines: list[tuple[int, str]] = []
        for line in raw_lines:
            # Отсекаем комментарии (# или ;)
            line = re.split(r"[#;]", line)[0].strip()
            if line:
                clean_lines.append((0, line))

        # --- Первый проход: построение таблицы меток ---
        instructions_pass1: list[str] = []
        current_address = 0

        for _, line in clean_lines:
            if line.endswith(":"):
                label_name = line[:-1].strip()
                if label_name in self.labels:
                    raise ValueError(f"Дублирование метки: {label_name}")
                self.labels[label_name] = current_address
            else:
                instructions_pass1.append(line)
                current_address += 1

        # --- Второй проход: кодирование команд в машинный код ---
        machine_code: list[int] = []

        for addr, line in enumerate(instructions_pass1):
            # Разделение мнемоники и операндов
            parts = line.replace(",", " ").split()
            mnemonic = parts[0].upper()
            args = parts[1:]

            if mnemonic not in MNEMONICS:
                raise ValueError(
                    f"Неизвестная команда: {mnemonic} на строке '{line}'"
                )

            opcode = MNEMONICS[mnemonic]
            word = 0

            match opcode:
                case Opcode.HALT:
                    word = opcode << 12

                case Opcode.MOVI:
                    # MOVI Rd, Imm9
                    rd = self._parse_register(args[0])
                    imm = self._parse_immediate(args[1])
                    word = (opcode << 12) | (rd << 9) | (imm & 0x1FF)

                case Opcode.MOV:
                    # MOV Rd, Rs
                    rd = self._parse_register(args[0])
                    rs = self._parse_register(args[1])
                    word = (opcode << 12) | (rd << 9) | (rs << 6)

                case Opcode.ADD | Opcode.SUB | Opcode.CMP | Opcode.AND:
                    # ADD Rd, Rs
                    rd = self._parse_register(args[0])
                    rs = self._parse_register(args[1])
                    word = (opcode << 12) | (rd << 9) | (rs << 6)

                case Opcode.LOAD:
                    # LOAD Rd, Rs (или LOAD Rd, [Rs])
                    rd = self._parse_register(args[0])
                    rs_str = args[1].strip("[]")
                    rs = self._parse_register(rs_str)
                    word = (opcode << 12) | (rd << 9) | (rs << 6)

                case Opcode.STORE:
                    # STORE Rd, Rs (или STORE [Rd], Rs)
                    rd_str = args[0].strip("[]")
                    rd = self._parse_register(rd_str)
                    rs = self._parse_register(args[1])
                    word = (opcode << 12) | (rd << 9) | (rs << 6)

                case Opcode.JMP | Opcode.JZ:
                    # JMP target_label / JMP offset
                    target = args[0]
                    if target in self.labels:
                        target_addr = self.labels[target]
                        # Относительное смещение: цель - (текущий адрес + 1)
                        offset = target_addr - (addr + 1)
                    else:
                        offset = self._parse_immediate(target)

                    word = (opcode << 12) | (offset & 0x1FF)

            machine_code.append(word & 0xFFFF)

        return machine_code