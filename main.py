from src.mini16 import CPU, Assembler, Memory


def print_cpu_state(step_num: int, cpu: CPU) -> None:
    regs = " | ".join(f"R{i}: {val:<4}" for i, val in enumerate(cpu.registers[:4]))
    flags = f"Z={int(cpu.flag_z)} N={int(cpu.flag_n)}"
    print(
        f"Такт {step_num:02d} | PC: 0x{cpu.pc:04X} | {regs} | Флаги: {flags} | Halted: {cpu.halted}"
    )


def main() -> None:
    # Исходный текст программы на ассемблере 
    source_code = """
        # Инициализация
        MOVI R0, 0       # R0 = Аккумулятор суммы
        MOVI R1, 5       # R1 = Счетчик (будем уменьшать от 5 до 0)
        MOVI R2, 1       # R2 = Шаг декремента (1)

    loop:
        ADD  R0, R1      # R0 = R0 + R1 (прибавляем текущий счетчик)
        SUB  R1, R2      # R1 = R1 - 1  (уменьшаем счетчик, выставляет флаг Z при 0)
        JZ   exit        # Если R1 == 0 (Z=1), выходим из цикла
        JMP  loop        # Иначе прыгаем обратно на метку loop

    exit:
        HALT             # Остановка 
    """

    # 1. Ассемблирование текста в машинный код
    asm = Assembler()
    machine_code = asm.assemble(source_code)

    print("Сгенерированный машинный код (hex):")
    print([f"0x{word:04X}" for word in machine_code])
    print("-" * 50)

    # 2. Инициализация аппаратуры
    ram = Memory()
    cpu = CPU(memory=ram)

    # 3. Загрузка собранного кода в ОЗУ
    ram.load_program(start_address=0, code=machine_code)

    print("=== Старт выполнения программы ===")
    step_counter = 1
    while not cpu.halted:
        current_pc = cpu.pc
        current_word = ram.read(current_pc)
        cpu.step()
        print(f"Такт {step_counter:02d} | Слово 0x{current_word:04X} с адреса 0x{current_pc:04X}")
        step_counter += 1

    print("=" * 50)
    print("Выполнение завершено.")
    print_cpu_state(step_counter, cpu)
    print(f"\nИтоговая сумма в R0: {cpu.registers[0]} (ожидается 15)")


if __name__ == "__main__":
    main()