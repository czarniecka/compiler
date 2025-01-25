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
        """
        Obsługuje instrukcję READ.
        """
        if isinstance(var, tuple):
            if var[0] == "UNDECLARED":
                if var[1] in self.symbol_table.iterators:
                    raise Exception(f"Unknown iterator {var[1]}.")
                else:
                    raise Exception(f"Unknown variable {var[1]}.")
            elif var[0] == "ARRAY":
                array_name, index = var[1], var[2]
                address = self.handle_array_index(array_name, index)
                if(address != 0):
                    self.emit(f"GET {address}")
                else:
                    self.emit(f"GET 0")
                    self.emit(f"STOREI 1")
        else:
            # Zwrócona nazwa pojedynczej zmiennej lub iteratora
            if var in self.symbol_table:
                self.symbol_table[var].initialized = True
                address = self.symbol_table.get_pointer(var)    
            else:
                address = self.symbol_table.get_iterator(var) #idk czy potrzeba tego else???
                
            self.emit(f"GET {address}")


    def handle_write(self, value):
        """
        Obsługuje instrukcję WRITE.
        """
        if value[0] == "ID":
            if isinstance(value[1], tuple):
                if value[1][0] == "UNDECLARED":
                    if value[1][1] in self.symbol_table.iterators:
                        iterator = self.symbol_table.get_iterator(value[1][1])
                        self.emit(f"PUT {iterator.base_memory_index}")
                    else:
                        raise Exception(f"Undeclared variable '{value[1][1]}'.")
                elif value[1][0] == "ARRAY":
                    array_name, index  = value[1][1], value[1][2]
                    address = self.handle_array_index(array_name, index)
                    if(address != 0):
                        self.emit(f"PUT {address}")
                    else:
                        self.emit(f"LOADI 1")
                        self.emit(f"PUT 0")
                else:
                    raise Exception(f"Invalid ID value '{value[1]}'.")
            else:
                variable = self.symbol_table.get_pointer(value[1])
                self.emit(f"PUT {variable}")
        elif value[0] == "NUM":
            self.emit(f"SET {value[1]}")
            self.emit(f"PUT 0")
        else:
            raise Exception(f"Unsupported value type '{value[0]}' for WRITE.")
        
    # Obsługa komendy ASSIGN
    def handle_assign(self, var, expression):
        """
        Obsługuje przypisanie wartości do zmiennej lub elementu tablicy.
        """
        # Generowanie kodu dla wyrażenia (prawa strona przypisania)
        #expr_code = self.generate_expression(expression)

        if isinstance(var, tuple):  # Jeżeli zmienna to np. tablica z indeksem
            if var[0] == "UNDECLARED":
                # Próba przypisania do niezadeklarowanej zmiennej lub iteratora
                if var[1] in self.symbol_table.iterators:
                    raise Exception(f"Cannot assign to iterator '{var[1]}'.")
                else:
                    raise Exception(f"Undeclared variable '{var[1]}'.")

            elif var[0] == "ARRAY":
                array_name, index  = var[1], var[2]
                address = self.handle_array_index(array_name, index)
                self.generate_expression(expression)
                if(address != 0):
                    self.emit(f"STORE {address}")
                else:
                    self.emit(f"STOREI 1")
        else:
            # Zwykła zmienna (x := ...)
            if isinstance(var, str):
            #if type(self.symbol_table[var]) == Variable:
                #self.symbol_table.add_variable(var)
                self.symbol_table[var].initialized = True
                adress = self.symbol_table.get_pointer(var)
                self.generate_expression(expression)
                self.emit(f"STORE {adress}")
            else:
                raise Exception(f"Assigning to array {var} with no index provided.")

    # Generowanie kodu dla wyrażeń
    def generate_expression(self, expression):
        if expression[0] == "NUM":  # Stała liczbowa
            self.emit(f"SET {expression[1]}")
        elif expression[0] == "ID":  # Zmienna
            self.handle_expressionID(expression[1])
        elif expression[0] == "PLUS":
            self.generate_expression(expression[1])
            self.emit(f"STORE 1")
            self.generate_expression(expression[2])
            self.emit(f"ADD 1")
        elif expression[0] == "MINUS":
            self.generate_expression(expression[2])
            self.emit(f"STORE 1")
            self.generate_expression(expression[1])
            self.emit(f"SUB 1")
        elif expression[0] == "MULTIPLY":
            self.handle_multiply(expression[1], expression[2]) 
        elif expression[0] == "DIVIDE":
            self.handle_division(expression[1], expression[2])
            self.emit("LOAD 3")  # Załaduj wynik do akumulatora
        elif expression[0] == "MOD":
            self.handle_division(expression[1], expression[2])
            self.emit("LOAD 5")  # Załaduj wynik do akumulatora
        else:
            raise ValueError(f"Unsupported expression type: {expression}")
    
    def handle_multiply(self, left_expr, right_expr):
        if right_expr[1] == 2:
            self.generate_expression(left_expr)
            self.emit("ADD 0")

        elif left_expr[1] == 2:
            self.generate_expression(right_expr)
            self.emit("ADD 0")
        else:
            self.emit("SET 0")
            self.emit("STORE 5")
            self.emit("SET 0")
            self.emit("STORE 6")

            self.generate_expression(left_expr)
            self.emit("JPOS 6")
            self.emit("STORE 1")
            # Flaga znaku
            self.emit("SET 1")
            self.emit("STORE 5")

            self.emit("SET 0")
            self.emit("SUB 1")

            self.emit("STORE 1") # Pierwsza zmienna do p1
            
            self.generate_expression(right_expr)
            self.emit("JPOS 6")
            self.emit("STORE 2")

            # Flaga znaku
            self.emit("SET -1")
            self.emit("STORE 6")

            self.emit("SET 0")
            self.emit("SUB 2")

            self.emit("STORE 2") # Druga zmienna do p2

            self.emit("SET 0")
            self.emit("STORE 3")  # Zapisz 0 do p3 jako wynik

            # Jeśli coś 0 to koniec pętli, wynik = 0
            self.emit("LOAD 1")
            self.emit("JZERO 14")
            self.emit("LOAD 2")
            self.emit("JZERO 12")

            # Pętla mnożenia
            self.emit("LOAD 2")          
            self.emit("JZERO 18")         
            ########################################
            self.emit("LOAD 2")
            self.emit("HALF")
            self.emit("STORE 4") # (_B/2_) do 4

            self.emit("LOAD 4")  
            self.emit("ADD 4")   # 2*(_B/2_)
            self.emit("SUB 2")
            self.emit("JZERO 4") # Wyszło 0 po odejmowaniu, to jump, bo B parzyste

            self.emit("LOAD 3")
            self.emit("ADD 1")
            self.emit("STORE 3")

            # 2*A
            self.emit("LOAD 1")
            self.emit("ADD 1")
            self.emit("STORE 1") 

            # B/2
            self.emit("LOAD 2")
            self.emit("HALF")
            self.emit("STORE 2") 
            ########################################
            self.emit(f"JUMP -18")  # Skocz do początku pętli

            # Sprawdzenie znaku
            self.emit("LOAD 5")
            self.emit("ADD 6")
            self.emit("JZERO 4")

            # Zmiana znaku wyniku, jesli różne znaki A i B
            self.emit("SET 0")
            self.emit("SUB 3")
            self.emit("STORE 3")

            self.emit("LOAD 3")  # Załaduj wynik do akumulatora

    def handle_division(self, left_expr, right_expr):
        if right_expr[1] == 2:
            self.generate_expression(left_expr)
            self.emit("HALF")
            #self.emit("STORE 3")
        #elif right_expr[1] == 1:
            #self.generate_expression(left_expr)
        else:
            # Zerowanie flag znaków
            self.emit("SET 0")
            self.emit("STORE 7")
            self.emit("SET 0")
            self.emit("STORE 8")

            self.generate_expression(left_expr)  # Dzielna
            self.emit("JPOS 6")
            self.emit("STORE 1")
            # Flaga znaku
            self.emit("SET 1")
            self.emit("STORE 7")

            self.emit("SET 0")
            self.emit("SUB 1")

            self.emit("STORE 1") # Dzielna do p1
            self.code.append("STORE 5") # Pomocnicza dzielna

            self.generate_expression(right_expr) # Dzielnik
            self.emit("JPOS 6")
            self.emit("STORE 2")

            # Flaga znaku
            self.emit("SET -1")
            self.emit("STORE 8")

            self.emit("SET 0")
            self.emit("SUB 2")

            self.emit("STORE 2") # Dzielnik do p2
            self.code.append("STORE 6") # Pomocniczy dzielnik

            # Inicjalizacja zmiennych w odpowiednich komórkach
            self.code.append("SET 0")   # set wynik = 0
            self.code.append("STORE 3")  

            self.code.append("SET 1")   # k = 1
            self.code.append("STORE 4")  

            # Jeśli coś 0 to koniec pętli, wynik = 0
            self.emit("LOAD 1")
            self.emit("JZERO 50")
            self.emit("LOAD 2")
            self.emit("JZERO 48")

            # Pierwsza pętla obliczeń
            self.code.append("LOAD 5")  
            self.code.append("SUB 6")     # a - b
            self.code.append("JPOS 3")    # jeśli a - b >= 0
            self.code.append("JZERO 2")   # jeśli a - b = 0
            self.code.append("JUMP 8")    

            # Dodajemy b do k i zapisujemy
            self.code.append("LOAD 6")
            self.code.append("ADD 6")     # b + b_mult
            self.code.append("STORE 6")   
            self.code.append("LOAD 4")
            self.code.append("ADD 4")     # k + k
            self.code.append("STORE 4")   
            self.code.append("JUMP -11")

            # Zmieniamy wartości pomocnicze (dzielimy przez 2)
            self.code.append("LOAD 4")
            self.code.append("HALF")      # k //= 2
            self.code.append("STORE 4")
            self.code.append("LOAD 6")
            self.code.append("HALF")      # b_mult //= 2
            self.code.append("STORE 6") 

            # Sprawdzamy warunki na mod
            self.code.append("LOAD 5")
            self.code.append("SUB 2")     # a - b
            self.code.append("JPOS 3")    # jeśli a - b >= 0
            self.code.append("JZERO 2")   # jeśli a - b = 0
            self.code.append("JUMP 19")   

            # Ponownie obliczamy resztę
            self.code.append("LOAD 5")
            self.code.append("SUB 6")     # a - b_mult
            self.code.append("JPOS 3")    # jeśli a - b_mult >= 0
            self.code.append("JZERO 2")   # jeśli a - b_mult = 0
            self.code.append("JUMP 7") 

            # Przechowujemy wynik w komórce 3
            self.code.append("LOAD 5")    
            self.code.append("SUB 6") 
            self.code.append("STORE 5")
            self.code.append("LOAD 3")

            self.code.append("ADD 4")     # dodaj k do res
            self.code.append("STORE 3")   
            # Dzielimy ponownie k i b_mult przez 2
            self.code.append("LOAD 4")
            self.code.append("HALF")      # k //= 2
            self.code.append("STORE 4") 
            self.code.append("LOAD 6")
            self.code.append("HALF")      # b_mult //= 2
            self.code.append("STORE 6")   

            self.code.append("JUMP -22")

            # Sprawdzenie znaku
            self.emit("LOAD 7")
            self.emit("ADD 8")
            self.emit("JZERO 4")
            # Zmiana znaku wyniku, jesli różne znaki A i B
            self.emit("SET 0")
            self.emit("SUB 3")
            self.emit("STORE 3")

            #Sprawdzenie znaku reszty z dzielenia
            self.emit("LOAD 8")
            self.emit("JZERO 4")
            # Zmiana znaku reszty, jesli B ujemne
            self.emit("SET 0")
            self.emit("SUB 5")
            self.emit("STORE 5")

    def handle_expressionID(self, arg_expression):
        if arg_expression[0] == "UNDECLARED":
            # Obsługa niezadeklarowanych zmiennych
            if arg_expression[1] in self.symbol_table.iterators:
                # Jeśli to iterator, pobierz jego adres i załaduj do akumulatora
                iterator_address = self.symbol_table.get_iterator(arg_expression[1])
                self.emit(f"LOAD {iterator_address}")
            else:
                raise Exception(f"Undeclared variable '{arg_expression[1]}'.")
        elif arg_expression[0] == "ARRAY":
            # Obsługa tablic
            array_name, index = arg_expression[1], arg_expression[2]

            # Obsługa indeksu tablicy
            address = self.handle_array_index(array_name, index)
            
            if address == 0:  # Użycie adresowania pośredniego
                self.emit(f"LOADI 1")  # Wartość w pamięci pod adresem w komórce 1
            else:
                self.emit(f"LOAD {address}")  # Wartość pod stałym adresem
        elif isinstance(arg_expression[0], str):
            variable_name = arg_expression[0]
            if variable_name in self.symbol_table:
                address = self.symbol_table.get_pointer(variable_name)
                self.emit(f"LOAD {address}")
            else:
                raise Exception(f"Unknown variable '{variable_name}'.")
        else:
            raise Exception(f"Invalid expression ID format: '{arg_expression}'.")


    def handle_array_index(self, array_name, index):
        first_index = self.symbol_table[array_name].first_index
        memory_of_first_index = self.symbol_table.get_pointer([array_name, first_index])
        array_offset = memory_of_first_index - first_index
        address = 0
        if isinstance(index, int):  # Stały indeks
            address = self.symbol_table.get_pointer([array_name, index])
        elif isinstance(index, tuple) and index[0] == "ID":
            if isinstance(index[1], tuple) and index[1][0] == "UNDECLARED":
                if index[1][1] in self.symbol_table.iterators:
                    iterator_address = self.symbol_table.get_iterator(index[1][1])
                    self.emit(f"SET {array_offset}")
                    self.emit(f"ADD {iterator_address}")
                    self.emit(f"STORE 1")
                    #TODO: sprawdzić, czy nie wyszło za zakres
                else:
                    raise Exception(f"Undeclared index variable '{index[1][1]}'.")
                
            elif isinstance(index[1], str):  # Znana zmienna
                variable_address = self.symbol_table.get_pointer(index[1])
                if not self.symbol_table[index[1]].initialized:
                    raise Exception(f"Index variable '{index[1]}' is not initialized.")
                self.emit(f"SET {array_offset}")
                self.emit(f"ADD {variable_address}")
                self.emit(f"STORE 1")
                #TODO: sprawdzić, czy nie wyszło za zakres
            else:
                raise Exception(f"Invalid index type '{index}'.")
        else:
            raise Exception(f"Unsupported index format '{index}'.")
        
        return address
