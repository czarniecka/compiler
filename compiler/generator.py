from symbol_table import Variable
class CodeGenerator:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table  # symbol_table to tablica symboli zawierająca informacje o zmiennych
        self.code = []  # przechowuje generowane instrukcje

    # Emitowanie kodu
    def emit(self, instruction):
        self.code.append(instruction)

    # Główna funkcja generowania kodu
    def generate(self, ast):
        if ast[0] == "PROGRAM":
            _, procedures, main = ast
            self.generate_procedures(procedures)
            self.generate_main(main)
            self.emit("HALT")
        return "\n".join(self.code)

    # Obsługa procedur (w przyszłości)
    def generate_procedures(self, procedures):
        for procedure in procedures:
            _, name, declarations, commands = procedure
            self.emit(f"{name}:")
            self.generate_commands(commands)
            self.emit("RTRN p0")  # Później obsłużyć odpowiednio

    # Obsługa sekcji MAIN
    def generate_main(self, main):
        if main[0] == "MAIN_DEC":
            _, declarations, commands = main
            self.generate_commands(commands)
        elif main[0] == "MAIN":
            _, commands = main
            self.generate_commands(commands)

    # Generowanie kodu dla listy komend
    def generate_commands(self, commands):
        for command in commands:
            self.generate_command(command)

    # Generowanie kodu dla pojedynczej komendy
    def generate_command(self, command):
        match command:
            case ("ASSIGN", var, expression):
                self.handle_assign(var, expression)
            case ("WRITE", value):
                self.handle_write(value)
            case ("READ", var):
                self.handle_read(var)
            case ("IF", condition, then_commands, constants):
                pass
            case ("IFELSE", condition, then_commands, else_commands, constants):
                pass
            case ("WHILE", condition, commands, constants):
                pass
            case ("REPEAT", commands, condition, constants):
                pass
            case ("FORTO", iterator, start, end, commands, constants):
                pass
            case ("FORDOWNTO", iterator, start, end, commands, constants):
                pass
            case ("PROC_CALL", name, args):
                pass

    def handle_read(self, var):
        if isinstance(var, tuple) and var[0] == "ARRAY":
            array_name, index = var[1], var[2]
            if isinstance(index, int):  # Stały indeks
                address = self.symbol_table.get_array_at(array_name, index)
                self.emit(f"GET 0")
                self.emit(f"STORE {address}")
            elif isinstance(index, tuple) and index[0] == "ID":
                index_address = self.symbol_table.get_pointer(index[1])
                base_address = self.symbol_table[array_name].base_memory_index
                self.emit(f"LOAD {index_address}")
                self.emit(f"ADD {base_address}")
                self.emit("STOREI 0")
            else:
                raise Exception(f"Unsupported index type '{index}'.")
        else:
            # Odczyt do zmiennej
            address = self.symbol_table.get_pointer(var)
            self.emit(f"GET 0")
            self.emit(f"STORE {address}")



    def handle_write(self, value):
        if value[0] == "ID" and isinstance(value[1], tuple) and value[1][0] == "ARRAY":
            array_name, index = value[1][1], value[1][2]
            if isinstance(index, int):  # Stały indeks
                address = self.symbol_table.get_array_at(array_name, index)
                self.emit(f"LOAD {address}")
            elif isinstance(index, tuple) and index[0] == "ID":
                index_address = self.symbol_table.get_pointer(index[1])
                base_address = self.symbol_table[array_name].base_memory_index
                self.emit(f"LOAD {index_address}")
                self.emit(f"ADD {base_address}")
                self.emit("LOADI 0")
            else:
                raise Exception(f"Unsupported index type '{index}'.")
            self.emit("PUT 0")
        elif value[0] == "NUM":
            self.emit(f"SET {value[1]}")
            self.emit("PUT 0")
        elif value[0] == "ID":
            address = self.symbol_table.get_pointer(value[1])
            self.emit(f"LOAD {address}")
            self.emit("PUT 0")
        else:
            raise Exception(f"Unsupported value type '{value}'.")

        
    #
    def handle_assign(self, var, expression):
        self.generate_expression(expression)  # Generowanie kodu dla prawej strony przypisania

        if isinstance(var, tuple) and var[0] == "ARRAY":
            array_name, index = var[1], var[2]
            if isinstance(index, int):  # Stały indeks
                address = self.symbol_table.get_array_at(array_name, index)
                self.emit(f"STORE {address}")
            elif isinstance(index, tuple) and index[0] == "ID":
                index_address = self.symbol_table.get_pointer(index[1])
                base_address = self.symbol_table[array_name].base_memory_index
                self.emit(f"LOAD {index_address}")
                self.emit(f"ADD {base_address}")
                self.emit("STOREI 0")
            else:
                raise Exception(f"Unsupported index type '{index}'.")
        else:
            address = self.symbol_table.get_pointer(var)
            self.emit(f"STORE {address}")


    # Generowanie kodu dla wyrażeń
    def generate_expression(self, expression):
        if expression[0] == "NUM":  # Stała liczbowa
            pass
        elif expression[0] == "ID":  # Zmienna
            pass
        else:
            raise ValueError(f"Unsupported expression type: {expression}")


    def handle_array_index(self, array_name, index):
        base_address = self.symbol_table[array_name].base_memory_index
        if isinstance(index, int):
            return base_address + index - self.symbol_table[array_name].first_index
        elif isinstance(index, tuple) and index[0] == "ID":
            index_address = self.symbol_table.get_pointer(index[1])
            self.emit(f"LOAD {index_address}")
            self.emit(f"ADD {base_address}")
            return None  # W tym przypadku adres będzie w akumulatorze
        else:
            raise Exception(f"Unsupported index format '{index}'.")

