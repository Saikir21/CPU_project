class Memory:
    SIZE: int = 65536  
    IO_STDOUT: int = 0xFF00  # Порт вывода символа в терминал (MMIO)

    def __init__(self) -> None:
        # Инициализация массива с 65536 нулями
        self._storage: list[int] = [0] * self.SIZE

    def read(self, address: int) -> int:
        """Считывает 16-битное слово по адресу."""
        self._check_address(address)
        return self._storage[address]

    def write(self, address: int, value: int) -> None:

        self._check_address(address)

        # Перехват MMIO: запись в терминал
        if address == self.IO_STDOUT:
            char_code = value & 0xFF  # Берем младший байт (ASCII-код)
            print(chr(char_code), end="", flush=True)
            return None

        # Гарантируем, что в ячейку физически попадет только 16 бит
        self._storage[address] = value & 0xFFFF

    def load_program(self, start_address: int, code: list[int]) -> None:
        # Загружает машинный код программы в память начиная со start_address
        for i, word in enumerate(code):
            target = start_address + i
            self.write(target, word)

    def _check_address(self, address: int) -> None:
        if not (0 <= address < self.SIZE):
            raise IndexError(
                f"Адрес 0x{address:04X} выходит за пределы допустимого диапазона"
            )