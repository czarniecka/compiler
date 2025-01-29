from symbol_table import Variable
class CodeGenerator:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table  # symbol_table to tablica symboli zawierająca informacje o zmiennych
        self.code = []  # przechowuje generowane instrukcje
        self.iterators = []

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

    # Obsługa procedur
    def generate_procedures(self, procedures):
        for procedure in procedures:
            if procedure[0] == "PROCEDURE_DEC":
                _, name_params, declarations, commands = procedure
                self.symbol_table.add_procedure(name_params[0], name_params[1], declarations, commands)
            elif procedure[0] == "PROCEDURE":
                _, name_params, commands = procedure
                self.symbol_table.add_procedure(name_params[0], name_params[1], [], commands) 

    def allocate_local_variables(self, declarations):
        local_addresses = []
        for var in declarations:
            address = self.symbol_table.add_variable(var[0][1])
            local_addresses.append(address)
        return local_addresses

    def free_local_variables(self, local_addresses):
        for address in local_addresses:
            self.symbol_table.remove_variable(address)


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
            case ("IF", condition, commands, constants):
                self.handle_if(condition, commands)
            case ("IFELSE", condition, then_commands, else_commands, constants):
                self.handle_ifelse(condition, then_commands, else_commands)
            case ("WHILE", condition, commands, constants):
                self.handle_while(condition, commands)
            case ("REPEAT", commands, condition, constants):
                self.handle_repeat(condition, commands)
            case ("FORTO", iterator, start, end, commands, constants):
                self.handle_for(iterator, start, end, commands, False, constants)
            case ("FORDOWNTO", iterator, start, end, commands, constants):
                self.handle_for(iterator, start, end, commands, True, constants)
            case ("PROC_CALL", name, args):
                if name in self.symbol_table.procedures:
                    _, _, params, local_variables, commands = self.symbol_table.get_procedure(name)

                    if len(args) != len(params):
                        raise Exception(f"Incorrect number of arguments for procedure {name}. Expected {len(params)}, got {len(args)}.")
                    
                    param_addresses = []
                    for (arg_value, param) in zip(args, params):
                        param_address = self.symbol_table.get_pointer(param)
                        self.handle_expressionID(arg_value)
                        self.emit(f"STORE {param_address}")
                        param_addresses.append(param_address)

                    self.generate_commands(commands)
                else: 
                    raise Exception(f"Unknown procedure {name}.")

    def handle_if(self, condition, commands):
        condition_return = self.simplify_condition(condition)
        if isinstance(condition_return, bool):
            if condition_return:
                self.generate_commands(commands)
        else:
            start_of_condition = len(self.code)
            self.check_condition(condition)
            start_of_command = len(self.code)
            self.generate_commands(commands)
            end_of_command = len(self.code)
            for i in range(start_of_condition, start_of_command):
                self.code[i] = self.code[i].replace('finish', str(end_of_command - i))

    def handle_ifelse(self, condition, then_commands, else_commands):
        condition_return = self.simplify_condition(condition)
        print(condition_return)
        if isinstance(condition_return, bool):
            if condition_return:
                self.generate_commands(then_commands)
            else:
                self.generate_commands(else_commands)
        else:
            start_of_condition = len(self.code)
            self.check_condition(condition)
            start_of_if = len(self.code)
            self.generate_commands(then_commands)
            self.emit(f"JUMP finish")
            start_of_else = len(self.code)
            self.generate_commands(else_commands)
            end_of_command = len(self.code)
            self.code[start_of_else - 1] = self.code[start_of_else - 1].replace('finish', str(end_of_command - start_of_else + 1))
            for i in range(start_of_condition, start_of_if):
                self.code[i] = self.code[i].replace('finish', str(start_of_else - i))

    def handle_while(self, condition, commands):
        condition_return = self.simplify_condition(condition)
        print(condition_return)
        if isinstance(condition_return, bool):
            if condition_return:
                #TODO: obsługa stałych
                start_of_loop = len(self.code)
                self.generate_commands(commands)
                self.emit(f"JUMP {start_of_loop - len(self.code)}")
        else:
            start_of_condition = len(self.code)
            self.check_condition(condition)
            start_of_loop = len(self.code)
            self.generate_commands(commands)
            self.code.append(f"JUMP {start_of_condition - len(self.code)}")
            loop_end = len(self.code)
            for i in range(start_of_condition, start_of_loop):
                self.code[i] = self.code[i].replace('finish', str(loop_end - i))

    def handle_repeat(self, condition, commands):
        print(commands)
        start_of_loop = len(self.code)
        self.generate_commands(commands)
        start_of_condition = len(self.code)
        self.check_condition(condition)
        end_of_condition = len(self.code)
        for i in range(start_of_condition, end_of_condition ):
            self.code[i] = self.code[i].replace('finish', str(2))
        self.emit(f"JUMP 2")
        self.emit(f"JUMP -{end_of_condition - start_of_loop + 1}")

    def handle_for(self, iterator, start, end, commands, downto, constants):
        # TODO: obsługa błędu: a > b przy to, a< b przy downto
        if start[0] == end[0] == "NUM":
            if start[1] > end[1] and downto == False:
                raise Exception(f"Invalid for loop scope.")
            elif start[1] < end[1] and downto == True:
                raise Exception(f"Invalid for loop scope.")

        if iterator in self.symbol_table:
            raise Exception(f"Overloading name of iterator {iterator}.")

        if self.iterators:
            address, bound_address = self.symbol_table.get_iterator(self.iterators[-1])
            self.emit(f"STORE {address}")
        else:
            self.prepere_constants(constants)
            

        if downto:
            operation = "SUB 11"
        else:
            operation = "ADD 11"

        self.iterators.append(iterator)
        
        start_addr, end_addr = self.symbol_table.add_iterator(iterator)
        print(self.symbol_table.get_iterator(iterator))
        print(self.symbol_table.is_iterator(iterator))


        self.emit("SET 1")
        self.emit("STORE 11")

        self.generate_expression(start)
        self.emit(f"STORE {start_addr}")
        self.generate_expression(end)
        self.emit(operation)
        self.emit(f"STORE {end_addr}")

        start_of_for = len(self.code)

        self.emit(f"LOAD {start_addr}")
        self.emit(f"SUB {end_addr}")

        it = len(self.code)
        
        self.generate_commands(commands)
        
        self.emit(f"LOAD {start_addr}")
        self.emit(operation)
        self.emit(f"STORE {start_addr}")

        end_of_for = len(self.code)
        self.code.insert(it, f"JZERO {end_of_for - start_of_for}")
        self.emit(f"JUMP -{end_of_for - start_of_for + 1}")

    def prepere_constants(self, constants):
        for const in constants:
            address = self.symbol_table.get_const(const)
            if address is None:
                address = self.symbol_table.add_const(const)
                self.emit(f"STORE {address}")
                

    def simplify_condition(self, condition):
        if condition[1][0] == "NUM" and condition[2][0] == "NUM":
            if condition[0] == "LEQ":
                return condition[1][1] <= condition[2][1]
            elif condition[0] == "GEQ":
                return condition[1][1] >= condition[2][1]
            elif condition[0] == "lESS":
                return condition[1][1] < condition[2][1]
            elif condition[0] == "GREATER":
                return condition[1][1] > condition[2][1]
            elif condition[0] == "EQUAL":
                return condition[1][1] == condition[2][1]
            elif condition[0] == "NEQUAL":
                return condition[1][1] != condition[2][1]
        elif condition[1] == condition[2]:
            if condition[0] in ["EQUAL", "LEQ", "GEQ"]:
                return True
            else:
                return False
        else:
            return condition

    def check_condition(self, condition):
        
        self.generate_expression(condition[2])
        self.emit("STORE 11")
        self.generate_expression(condition[1])
        self.emit("SUB 11")

        match condition[0]:
            case ("GREATER"):
                self.emit("JPOS 2")
                self.emit("JUMP finish")
            case ("LESS"):
                self.emit("JNEG 2")
                self.emit("JUMP finish")
            case ("GEQ"):
                self.emit("JPOS 3")
                self.emit("JZERO 2")
                self.emit("JUMP finish")
            case ("LEQ"):
                self.emit("JNEG 3")
                self.emit("JZERO 2")
                self.emit("JUMP finish")
            case ("EQUAL"):
                self.emit("JZERO 2")
                self.emit("JUMP finish")
            case ("NEQUAL"):
                self.emit("JZERO 2")
                self.emit("JUMP 2")
                self.emit("JUMP finish")


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
                address = self.handle_array_index(array_name, index, 14)
                if(address != 0):
                    self.emit(f"GET {address}")
                else:
                    self.emit(f"GET 0")
                    self.emit(f"STOREI 14")
        else:
            # Zwrócona nazwa pojedynczej zmiennej lub iteratora
            if var in self.symbol_table:
                self.symbol_table[var].initialized = True
                address = self.symbol_table.get_pointer(var)    
            else:
                address, add2 = self.symbol_table.get_iterator(var) #idk czy potrzeba tego else???
                
            self.emit(f"GET {address}")


    def handle_write(self, value):
        """
        Obsługuje instrukcję WRITE.
        """
        if value[0] == "ID":
            if isinstance(value[1], tuple):
                if value[1][0] == "UNDECLARED":
                    if value[1][1] in self.symbol_table.iterators:
                        iterator, add2 = self.symbol_table.get_iterator(value[1][1])
                        self.emit(f"PUT {iterator.base_memory_index}")
                    else:
                        raise Exception(f"Undeclared variable '{value[1][1]}'.")
                elif value[1][0] == "ARRAY":
                    array_name, index  = value[1][1], value[1][2]
                    address = self.handle_array_index(array_name, index, 14)
                    if(address != 0):
                        self.emit(f"PUT {address}")
                    else:
                        self.emit(f"LOADI 14")
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
        if isinstance(var, tuple):  # Jeżeli zmienna to np. tablica z indeksem
            if var[0] == "UNDECLARED":
                # Próba przypisania do niezadeklarowanej zmiennej lub iteratora
                if var[1] in self.symbol_table.iterators:
                    raise Exception(f"Cannot assign to iterator '{var[1]}'.")
                else:
                    raise Exception(f"Undeclared variable '{var[1]}'.")

            elif var[0] == "ARRAY":
                array_name, index  = var[1], var[2]
                address = self.handle_array_index(array_name, index, 14)
                self.generate_expression(expression)
                if(address != 0):
                    self.emit(f"STORE {address}")
                else:
                    self.emit(f"STOREI 14")
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
            #self.emit("STORE 5")
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
            self.emit("SET 1")
            #self.emit("STORE 7")
            self.emit("STORE 9")
            # Zerowanie flag znaków
            self.emit("SET 0")
            #self.emit("STORE 7")
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
            self.emit("STORE 5") # Pomocnicza dzielna

            self.generate_expression(right_expr) # Dzielnik
            self.emit("JPOS 6")
            self.emit("STORE 2")

            # Flaga znaku
            self.emit("SET -1")
            self.emit("STORE 8")

            self.emit("SET 0")
            self.emit("SUB 2")

            self.emit("STORE 2") # Dzielnik do p2
            self.emit("STORE 6") # Pomocniczy dzielnik

            # Inicjalizacja zmiennych w odpowiednich komórkach
            self.emit("SET 0")   # set wynik = 0
            self.emit("STORE 3")  

            self.emit("SET 1")   # k = 1
            self.emit("STORE 4")  

            # Jeśli coś 0 to koniec pętli, wynik = 0
            self.emit("LOAD 1")
            self.emit("JZERO 50")
            self.emit("LOAD 2")
            self.emit("JZERO 48")

            # Pętla
            self.emit("LOAD 5")
            self.emit("SUB 6")     # a - b
            self.emit("JPOS 3")    # jeśli a - b >= 0
            self.emit("JZERO 2")   # jeśli a - b = 0
            self.emit("JUMP 8")    

            # Dodajemy b do k i zapisujemy
            self.emit("LOAD 6")
            self.emit("ADD 6")     # b + b_mult
            self.emit("STORE 6")   
            self.emit("LOAD 4")
            self.emit("ADD 4")     # k + k
            self.emit("STORE 4")   
            self.emit("JUMP -11")

            # Zmieniamy wartości pomocnicze (dzielimy przez 2)
            self.emit("LOAD 4")
            self.emit("HALF")      # k //= 2
            self.emit("STORE 4")
            self.emit("LOAD 6")
            self.emit("HALF")      # b_mult //= 2
            self.emit("STORE 6") 

            # Sprawdzamy warunki na mod
            self.emit("LOAD 5")
            self.emit("SUB 2")     # a - b
            self.emit("JPOS 3")    # jeśli a - b >= 0
            self.emit("JZERO 2")   # jeśli a - b = 0
            self.emit("JUMP 19")   

            # Ponownie obliczamy resztę
            self.emit("LOAD 5")
            self.emit("SUB 6")     # a - b_mult
            self.emit("JPOS 3")    # jeśli a - b_mult >= 0
            self.emit("JZERO 2")   # jeśli a - b_mult = 0
            self.emit("JUMP 7") 

            # Przechowujemy wynik w komórce 3
            self.emit("LOAD 5")    
            self.emit("SUB 6") 
            self.emit("STORE 5")
            self.emit("LOAD 3")

            self.emit("ADD 4")     # dodaj k do res
            self.emit("STORE 3")   
            # Dzielimy ponownie k i b_mult przez 2
            self.emit("LOAD 4")
            self.emit("HALF")      # k //= 2
            self.emit("STORE 4") 
            self.emit("LOAD 6")
            self.emit("HALF")      # b_mult //= 2
            self.emit("STORE 6")   

            self.emit("JUMP -22")


            # Sprawdzenie znaku
            self.emit("LOAD 7")
            self.emit("ADD 8")
            self.emit("JZERO 10") # jak 0 to skaczemy ten sam znak
            # Zmiana znaku wyniku, jesli różne znaki A i B
            self.emit("LOAD 2")
            self.emit("SUB 5")
            self.emit("STORE 5")

            self.emit("LOAD 3")
            self.emit("ADD 9")
            self.emit("STORE 3")
            self.emit("SET 0")
            self.emit("SUB 3")
            self.emit("STORE 3")

            #Sprawdzenie znaku reszty z dzielenia ############################################################3
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
                iterator_address, add2 = self.symbol_table.get_iterator(arg_expression[1])
                self.emit(f"LOAD {iterator_address}")
            else:
                raise Exception(f"Undeclared variable '{arg_expression[1]}'.")
        elif arg_expression[0] == "ARRAY":
            # Obsługa tablic
            array_name, index = arg_expression[1], arg_expression[2]

            # Obsługa indeksu tablicy
            address = self.handle_array_index(array_name, index, 15)
            
            if address == 0:  # Użycie adresowania pośredniego
                self.emit(f"LOADI 15")  # Wartość w pamięci pod adresem w komórce 1
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


    def handle_array_index(self, array_name, index, memory_cell):
        first_index = self.symbol_table[array_name].first_index
        memory_of_first_index = self.symbol_table.get_pointer([array_name, first_index])
        array_offset = memory_of_first_index - first_index
        address = 0
        if isinstance(index, int):  # Stały indeks
            address = self.symbol_table.get_pointer([array_name, index])
        elif isinstance(index, tuple) and index[0] == "ID":
            if isinstance(index[1], tuple) and index[1][0] == "UNDECLARED":
                if index[1][1] in self.symbol_table.iterators:
                    iterator_address, add2 = self.symbol_table.get_iterator(index[1][1])
                    self.emit(f"SET {array_offset}")
                    self.emit(f"ADD {iterator_address}")
                    self.emit(f"STORE {memory_cell}")
                    #TODO: sprawdzić, czy nie wyszło za zakres
                else:
                    raise Exception(f"Undeclared index variable '{index[1][1]}'.")
                
            elif isinstance(index[1], str):  # Znana zmienna
                
                variable_address = self.symbol_table.get_pointer(index[1])
                if not self.symbol_table[index[1]].initialized:
                    raise Exception(f"Index variable '{index[1]}' is not initialized.")
                self.emit(f"SET {array_offset}")
                self.emit(f"ADD {variable_address}")
                self.emit(f"STORE {memory_cell}")
                #TODO: sprawdzić, czy nie wyszło za zakres
            else:
                raise Exception(f"Invalid index type '{index}'.")
        else:
            raise Exception(f"Unsupported index format '{index}'.")
        
        return address