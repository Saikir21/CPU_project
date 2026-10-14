from src.mini16.cpu import CPU
from src.mini16.memory import Memory


def print_cpu_state(step_num: int, cpu: CPU) -> None:
    regs = " | ".join(f"R{i}: {val:<4}" for i, val in enumerate(cpu.registers[:4]))
    flags = f"Z={int(cpu.flag_z)} N={int(cpu.flag_n)}"
    print(
        f"Такт {step_num:02d} | PC: 0x{cpu.pc:04X} | {regs} | Флаги: {flags} | Halted: {cpu.halted}"
    )


def main() -> None:
    ram = Memory()
    cpu = CPU(memory=ram)

    # R0 = 10; R1 = 25; R0 = R0 + R1; HALT
    program = [
        0x100A,  # MOVI R0, 10
        0x1219,  # MOVI R1, 25
        0x3040,  # ADD  R0, R1
        0x0000,  # HALT
    ]

    # Загрузка программы в память начиная с адреса 0x0000
    ram.load_program(start_address=0, code=program)

    print("=== Начальное состояние ===")
    print_cpu_state(0, cpu)
    print("===========================")

    # Потактовое выполнение (Fetch-Decode-Execute)
    step_counter = 1
    while not cpu.halted:
        current_pc = cpu.pc
        current_word = ram.read(current_pc)
        cpu.step()
        print(f"Выполнено слово 0x{current_word:04X} с адреса 0x{current_pc:04X}")
        print_cpu_state(step_counter, cpu)
        print("-" * 50)
        step_counter += 1

    print("\nПроцессор успешно завершил работу.")
    print(f"Итоговый результат в R0: {cpu.registers[0]}")


if __name__ == "__main__":
    main()