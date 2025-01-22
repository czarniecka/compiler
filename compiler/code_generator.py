from symbol_table import Variable
class CodeGenerator:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table  # symbol_table to tablica symboli zawierająca informacje o zmiennych
        self.code = []  # przechowuje generowane instrukcje
        self.label_counter = 0


    # Generowanie unikalnych etykiet
    def generate_label(self):
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label

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
        """
        Obsługuje instrukcję READ.
        """
        if isinstance(var, tuple):
            if var[0] == "UNDECLARED":
                if var[1] in self.symbols.iterators:
                    raise Exception(f"Reading to iterator {var[1]}.")
                else:
                    raise Exception(f"Reading to undeclared variable {var[1]}.")
            elif var[0] == "ARRAY":
                array_name, index = var[1], var[2]
                address = self.symbol_table.get_array_at(array_name, index)
                self.emit(f"GET {address}")
        else:
            address = self.symbol_table.get_variable(var)
            self.emit(f"GET {address}")


    def handle_write(self, value):
        """
        Obsługuje instrukcję WRITE.
        """
        if value[0] == "ID":
            # Zmienna lub element tablicy
            if isinstance(value[1], tuple):
                # Sprawdzenie, czy wartość to nieznana zmienna lub iterator
                if value[1][0] == "UNDECLARED":
                    if value[1][1] in self.symbol_table.iterators:
                        # Jeśli to iterator
                        iterator = self.symbol_table.get_iterator(value[1][1])
                        self.emit(f"LOAD {iterator.base_memory_index}")
                    else:
                        raise Exception(f"ERROR: Undeclared variable '{value[1][1]}'.")
                elif value[1][0] == "ARRAY":
                    # Jeśli to element tablicy
                    array_name = value[1][1]
                    index = value[1][2]
                    self.handle_array_access(array_name, index)
                else:
                    raise Exception(f"ERROR: Invalid ID value '{value[1]}'.")
            else:
                # Zwykła zmienna
                variable = self.symbol_table.get_variable(value[1])
                self.emit(f"LOAD {variable.base_memory_index}")

        elif value[0] == "NUM":
            # Jeśli to stała liczba
            self.emit(f"SET {value[1]}")

        else:
            # Nieznany typ wartości
            raise Exception(f"ERROR: Unsupported value type '{value[0]}' for WRITE.")

        # Zawsze wypisujemy zawartość akumulatora
        self.emit("PUT 0")


    # Obsługa komendy ASSIGN
    def handle_assign(self, var, expression):
        """
        Obsługuje przypisanie wartości do zmiennej lub elementu tablicy.
        """
        # Generowanie kodu dla wyrażenia (prawa strona przypisania)
        expr_code = self.generate_expression(expression)

        if isinstance(var, tuple):  # Jeżeli zmienna to np. tablica z indeksem
            if var[0] == "UNDECLARED":
                # Próba przypisania do niezadeklarowanej zmiennej lub iteratora
                if var[1] in self.symbol_table.iterators:
                    raise Exception(f"Cannot assign to iterator '{var[1]}'.")
                else:
                    raise Exception(f"Undeclared variable '{var[1]}'.")

            elif var[0] == "ARRAY":
                # Przypadek przypisania do elementu tablicy
                array_name = var[1]
                index = var[2]

                # Obsługa indeksu tablicy
                if isinstance(index, tuple) and index[0] == "ID":
                    # Indeks jest identyfikatorem (np. `tab[i]`)
                    index_code = self.generate_expression(index)
                    self.emit(f"LOAD {index_code}")
                    self.emit(f"ADD {self.symbol_table[array_name].base_memory_index}")
                    self.emit("STORE 1")  # Zapisz obliczony adres w rejestrze 1
                    self.emit("STOREI 1")  # Przypisz wartość do obliczonego adresu
                elif isinstance(index, int):
                    # Indeks jest liczbą stałą (np. `tab[3]`)
                    array = self.symbol_table.get_array_at(array_name, index)
                    self.emit(f"STORE {array}")
                else:
                    raise Exception(f"Invalid index type for array '{array_name}'.")

            else:
                raise Exception(f"Invalid assignment to {var}.")
        else:
            # Zwykła zmienna (np. `x := ...`)
            adress = self.symbol_table.get_variable(var)
            self.emit(f"STORE {adress}")


    #TODO: do poprawy    
    # Generowanie kodu dla wyrażeń
    def generate_expression(self, expression):
        if expression[0] == "NUM":  # Stała liczbowa
            return f"LOADI {expression[1]}"
        elif expression[0] == "ID":  # Zmienna
            var_name = expression[1]
            address = self.symbol_table[var_name]
            return f"LOAD {address}"
        else:
            raise ValueError(f"Unsupported expression type: {expression}")
