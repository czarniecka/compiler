from symbol_table import Variable, Array
class CodeGenerator:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.code = []  
        self.iterators = []
        self.symbol_table.current_procedure = None
        self.previous_procedure = None

        self.ACCUMULATOR = 0
        self.LEFT_EXPR = 1
        self.RIGHT_EXPR = 2
        self.RESULT = 3
        self.FLAG_SIGN_LEFT_EXPR = 4
        self.FLAG_SIGN_RIGHT_EXPR = 5
        self.HELP = 6
        self.RESULT_MODULO = 7
        self.HELP_B = 8
        self.VALUE_ONE = 9
        self.CELL_CONDITION = 10
        self.ARRAY_POINTER = 11
        self.ARRAY_POINTER_EXPR = 12


    def emit(self, instruction):
        self.code.append(instruction)


    def generate(self, ast):
        if ast[0] == "PROGRAM":
            _, procedures, main = ast
            print(ast)
            jump_to_main = len(self.code)
            self.emit("JUMP to_main")
            self.generate_procedures(procedures)
            main_start = len(self.code)
            self.code[jump_to_main] = f"JUMP {main_start}"
            self.generate_main(main)
            self.emit("HALT")
        return "\n".join(self.code)


    def generate_procedures(self, procedures):
        
        defined_procedures = set()
        
        for procedure in procedures:
            if procedure[0] == "PROCEDURE":
                _, proc_head, declarations, commands = procedure
                name, params = proc_head
                
                if name in defined_procedures:
                    raise Exception(f"Procedure {name} redefined.")
                defined_procedures.add(name)

                # Sprawdzanie prefiksu 'T' dla tablic
                for param in params:
                    if isinstance(param, tuple) and not param[0].startswith("T"):
                        raise Exception(f"Array parameter {param} must start with 'T'.")
                      
                self.symbol_table.add_procedure(name, params, declarations, commands)
                
                self.symbol_table.current_procedure = name

                proc_start = len(self.code)

                if self.symbol_table.procedures[name].base_memory_index is None:
                    self.symbol_table.procedures[name].base_memory_index = proc_start

                self.generate_commands(commands)
                procedure = self.symbol_table.procedures[name]

                if procedure.call_count >= len(procedure.return_registers):
                    raise Exception(f"Exceeded maximum call count for procedure {name}.")
                return_memory_index = procedure.return_registers[procedure.call_count]

                self.emit(f"RTRN {return_memory_index}")

                self.symbol_table.current_procedure = None
      

    def generate_main(self, main):
        if main[0] == "MAIN_DEC":
            _, declarations, commands = main
            self.generate_commands(commands)
        elif main[0] == "MAIN":
            _, commands = main
            self.generate_commands(commands)


    def generate_commands(self, commands):
        for command in commands:
            self.generate_command(command)


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
            case ("PROC_CALL", name, args, line):
                self.handle_proc_call(name, args, line)


    def handle_proc_call(self, name, args, line):
        self.previous_procedure = self.symbol_table.current_procedure

        if name not in self.symbol_table.procedures:
            raise Exception(f"Unknown procedure {name} on line {line}.")
            
        for arg in args:
            if arg not in self.symbol_table:
                raise Exception(f"Undeclared argument {arg} on line {line}.")
            
        if name == self.symbol_table.current_procedure:
            raise Exception(f"Recursive call detected in procedure {name} on line {line}.")
                    
        self.symbol_table.current_procedure = name
        _, _, params, local_variables, commands = self.symbol_table.get_procedure(self.symbol_table.current_procedure)   

        if len(args) != len(params):
            raise Exception(f"Incorrect number of arguments for procedure {name}. Expected {len(params)}, got {len(args)} on line {line}.")
        
        for (param_name, param_obj), arg in zip(params.items(), args):
            if isinstance(param_obj, Array):  
                if arg not in self.symbol_table or not isinstance(self.symbol_table[arg], Array):
                    raise Exception(f"Expected array for parameter '{param_name}', but got variable '{arg}' on line {line}.")
            else: 
                if arg in self.symbol_table and isinstance(self.symbol_table[arg], Array):
                    raise Exception(f"Expected variable for parameter '{param_name}', but got array '{arg}' on line {line}.")

        for param, arg in zip(params, args):
            param_address = params[param]  
            arg_address = self.symbol_table.get_pointer(arg)  
            self.emit(f"SET {arg_address}")  
            self.emit(f"STORE {param_address}")
        
        procedure = self.symbol_table.procedures[name]
        if procedure.call_count >= 100:
            raise Exception(f"Exceeded maximum call count for procedure {name} on line {line}.")

        return_memory_index = procedure.return_registers[procedure.call_count]
        procedure.call_count += 1
        
        self.emit(f"SET {len(self.code) + 3}")
        self.emit(f"STORE {return_memory_index}")
        proc_base = procedure.base_memory_index
        self.emit(f"JUMP {proc_base - len(self.code)}")
        procedure.call_count -= 1

        if self.previous_procedure:
            self.symbol_table.current_procedure = self.previous_procedure
        else:
            self.symbol_table.current_procedure = None


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
        if isinstance(condition_return, bool):
            if condition_return:
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
        # TODO: obsługa błędu: a > b przy to, a < b przy downto
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
            operation = f"SUB {self.VALUE_ONE}"
        else:
            operation = f"ADD {self.VALUE_ONE}"

        self.iterators.append(iterator)
        start_addr, end_addr = self.symbol_table.add_iterator(iterator)

        self.emit("SET 1")
        self.emit(f"STORE {self.VALUE_ONE}")

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
            elif condition[0] == "LESS":
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
        self.emit(f"STORE {self.CELL_CONDITION}")
        self.generate_expression(condition[1])
        self.emit(f"SUB {self.CELL_CONDITION}")

        match condition[0]:
            case ("GREATER"):
                self.emit("JPOS 2")
                self.emit("JUMP finish")
            case ("LESS"):
                self.emit("JNEG 2")
                self.emit("JUMP finish")
            case ("GEQ"):
                self.emit(f"JPOS 3")
                self.emit("JZERO 2")
                self.emit("JUMP finish")
            case ("LEQ"):
                self.emit(f"JNEG 3")
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
        if isinstance(var, tuple):
            if var[0] == "UNDECLARED":
                if var[1] in self.symbol_table.iterators:
                    raise Exception(f"Unknown iterator {var[1]}.")
                else:
                    addr = self.symbol_table.get_pointer_proc(var[1][1])
                    if isinstance(self.symbol_table.get_pointer_proc(var[1][1]), Variable):
                        self.emit(f"GET {self.ACCUMULATOR}")
                        self.emit(f"STOREI {addr}")  
                    else:
                        raise Exception(f"Undeclared variable '{var[1][1]}'.")
                    
            elif var[0] == "ARRAY":
                array_name, index = var[1], var[2]
                address = self.handle_array_index(array_name, index, var[3], self.ARRAY_POINTER)
                if(address != 0):
                    self.emit(f"GET {address}")
                else:
                    self.emit(f"GET {self.ACCUMULATOR}")
                    self.emit(f"STOREI {self.ARRAY_POINTER}")
        else:
            if var in self.symbol_table:
                self.symbol_table[var].initialized = True
                address = self.symbol_table.get_pointer(var)    
            else:
                address, add2 = self.symbol_table.get_iterator(var) 
                
            self.emit(f"GET {address}")


    def handle_write(self, value):
        if value[0] == "ID":
            if isinstance(value[1], tuple):
                if value[1][0] == "UNDECLARED":
                    if value[1][1] in self.symbol_table.iterators:
                        iterator, add2 = self.symbol_table.get_iterator(value[1][1])
                        self.emit(f"PUT {iterator.base_memory_index}")
                    else:
                        addr = self.symbol_table.get_pointer_proc(value[1][1])
                        if isinstance(self.symbol_table.get_pointer_proc(value[1][1]), Variable):
                            self.emit(f"LOADI {addr}")  
                            self.emit(f"PUT 0")
                        else:
                            raise Exception(f"Undeclared variable '{value[1][1]}'.")
                elif value[1][0] == "ARRAY":
                    array_name, index  = value[1][1], value[1][2]
                    address = self.handle_array_index(array_name, index, value[1][2], self.ARRAY_POINTER)
                    if(address != 0):
                        self.emit(f"PUT {address}")
                    else:
                        self.emit(f"LOADI {self.ARRAY_POINTER}")
                        self.emit(f"PUT {self.ACCUMULATOR}")
                else:
                    raise Exception(f"Invalid ID value '{value[1]}'.")
            else:
                variable = self.symbol_table.get_pointer(value[1])
                self.emit(f"PUT {variable}")
        elif value[0] == "NUM":
            self.emit(f"SET {value[1]}")
            self.emit(f"PUT {self.ACCUMULATOR}")
        else:
            raise Exception(f"Unsupported value type '{value[0]}' for WRITE.")
        

    def handle_assign(self, var, expression):   
        if isinstance(var, tuple): 
            if var[0] == "UNDECLARED":
                if var[1] in self.symbol_table.iterators:
                    raise Exception(f"Cannot assign to iterator '{var[1]}' on line {var[2]}.")
                else:
                    address = self.symbol_table.get_pointer_proc(var[1])
                    self.generate_expression(expression)
                    if isinstance(self.symbol_table.get_pointer_proc(var[1]), Variable):
                        self.emit(f"STOREI {address}")
                    else:
                        self.emit(f"STORE {address}")  

            elif var[0] == "ARRAY":
                
                array_name, index  = var[1], var[2]
                address = self.handle_array_index(array_name, index, var[3], self.ARRAY_POINTER)
                
                self.generate_expression(expression)
                if(address != 0):
                    self.emit(f"STORE {address}")
                else:
                    self.emit(f"STOREI {self.ARRAY_POINTER}")
        else:
            if isinstance(var, str):

                self.symbol_table[var].initialized = True
                adress = self.symbol_table.get_pointer(var)

                self.generate_expression(expression)
                self.emit(f"STORE {adress}")
            else:
                raise Exception(f"Assigning to array {var} with no index provided on line {var[2]}.")


    def generate_expression(self, expression):

        if expression[0] == "NUM":  
            self.emit(f"SET {expression[1]}")
        elif expression[0] == "ID":  
            self.handle_expressionID(expression[1])
        elif expression[0] == "PLUS":
            self.generate_expression(expression[1])
            self.emit(f"STORE {self.LEFT_EXPR}")
            self.generate_expression(expression[2])
            self.emit(f"ADD {self.LEFT_EXPR}")
        elif expression[0] == "MINUS":
            self.generate_expression(expression[2])
            self.emit(f"STORE {self.LEFT_EXPR}")
            self.generate_expression(expression[1])
            self.emit(f"SUB {self.LEFT_EXPR}")
        elif expression[0] == "MULTIPLY":
            self.handle_multiply(expression[1], expression[2]) 
        elif expression[0] == "DIVIDE":
            self.handle_division(expression[1], expression[2])
            self.emit(f"LOAD {self.RESULT}") 
        elif expression[0] == "MOD":
            self.handle_division(expression[1], expression[2])
            self.emit(f"LOAD {self.RESULT_MODULO}") 
        else:
            raise ValueError(f"Unsupported expression type: {expression}")


    def handle_multiply(self, left_expr, right_expr):
        if right_expr[1] == 2:
            self.generate_expression(left_expr)
            self.emit(f"ADD {self.ACCUMULATOR}")
        elif left_expr[1] == 2:
            self.generate_expression(right_expr)
            self.emit(f"ADD {self.ACCUMULATOR}")
        else:
            self.emit("SET 0")
            self.emit(f"STORE {self.FLAG_SIGN_LEFT_EXPR}")
            self.emit(f"STORE {self.FLAG_SIGN_RIGHT_EXPR}")

            self.generate_expression(left_expr)
            self.emit("JPOS 6")
            self.emit(f"STORE {self.LEFT_EXPR}")
            # Flaga znaku
            self.emit("SET 1")
            self.emit(f"STORE {self.FLAG_SIGN_LEFT_EXPR}")

            self.emit("SET 0")
            self.emit(f"SUB {self.LEFT_EXPR}")

            self.emit(f"STORE {self.LEFT_EXPR}") 
            
            self.generate_expression(right_expr)
            self.emit("JPOS 6")
            self.emit(f"STORE {self.RIGHT_EXPR}")

            # Flaga znaku
            self.emit("SET -1")
            self.emit(f"STORE {self.FLAG_SIGN_RIGHT_EXPR}")

            self.emit("SET 0")
            self.emit(f"SUB {self.RIGHT_EXPR}")

            self.emit(f"STORE {self.RIGHT_EXPR}")

            self.emit("SET 0")
            self.emit(f"STORE {self.RESULT}") 

            # Jeśli coś 0 to koniec pętli, wynik = 0
            self.emit(f"LOAD {self.LEFT_EXPR}")
            self.emit("JZERO 14")
            self.emit(f"LOAD {self.RIGHT_EXPR}")
            self.emit("JZERO 12")

            # Pętla mnożenia
            self.emit(f"LOAD {self.RIGHT_EXPR}")          
            self.emit("JZERO 18")         

            self.emit(f"LOAD {self.RIGHT_EXPR}")
            self.emit("HALF")
            self.emit(f"STORE {self.HELP}") # (_B/2_) do 4

            self.emit(f"LOAD {self.HELP}")  
            self.emit(f"ADD {self.HELP}")   # 2*(_B/2_)
            self.emit(f"SUB {self.RIGHT_EXPR}")
            self.emit("JZERO 4") # Wyszło 0 po odejmowaniu, to jump, bo B parzyste

            self.emit(f"LOAD {self.RESULT}")
            self.emit(f"ADD {self.LEFT_EXPR}")
            self.emit(f"STORE {self.RESULT}")

            # 2*A
            self.emit(f"LOAD {self.LEFT_EXPR}")
            self.emit(f"ADD {self.LEFT_EXPR}")
            self.emit(f"STORE {self.LEFT_EXPR}") 

            # B/2
            self.emit(f"LOAD {self.RIGHT_EXPR}")
            self.emit("HALF")
            self.emit(f"STORE {self.RIGHT_EXPR}") 

            self.emit(f"JUMP -18")  # Skocz do początku pętli

            # Sprawdzenie znaku
            self.emit(f"LOAD {self.FLAG_SIGN_LEFT_EXPR}")
            self.emit(f"ADD {self.FLAG_SIGN_RIGHT_EXPR}")
            self.emit("JZERO 4")

            # Zmiana znaku wyniku, jesli różne znaki A i B
            self.emit("SET 0")
            self.emit(f"SUB {self.RESULT}")
            self.emit(f"STORE {self.RESULT}")

            self.emit(f"LOAD {self.RESULT}")  


    def handle_division(self, left_expr, right_expr):
        # w modulo nie działa, więc poprawić, albo wywalić
        if right_expr[1] == "heheheheheheh":
            self.generate_expression(left_expr)
            self.emit("HALF")
            self.emit(f"STORE {self.RESULT}")
        else:
            self.emit("SET 1")
            self.emit(f"STORE {self.VALUE_ONE}")

            # Zerowanie flag znaków
            self.emit("SET 0")
            self.emit(f"STORE {self.FLAG_SIGN_LEFT_EXPR}")
            self.emit(f"STORE {self.FLAG_SIGN_RIGHT_EXPR}")

            self.generate_expression(left_expr) 
            self.emit("JPOS 6")
            self.emit(f"STORE {self.LEFT_EXPR}")

            # Flaga znaku
            self.emit("SET 1")
            self.emit(f"STORE {self.FLAG_SIGN_LEFT_EXPR}")

            self.emit("SET 0")
            self.emit(f"SUB {self.LEFT_EXPR}")

            self.emit(f"STORE {self.LEFT_EXPR}") 
            self.emit(f"STORE {self.RESULT_MODULO}") 

            self.generate_expression(right_expr)
            self.emit("JPOS 6")
            self.emit("STORE 2")

            # Flaga znaku
            self.emit("SET -1")
            self.emit(f"STORE {self.FLAG_SIGN_RIGHT_EXPR}")

            self.emit("SET 0")
            self.emit("SUB 2")

            self.emit("STORE 2") 
            self.emit(f"STORE {self.HELP_B}") 

            self.emit("SET 0") 
            self.emit(f"STORE {self.RESULT}")  

            self.emit("SET 1") 
            self.emit(f"STORE {self.HELP}")  

            # Jeśli coś 0 to koniec pętli, wynik = 0
            self.emit(f"LOAD {self.LEFT_EXPR}")
            self.emit("JZERO 50")
            self.emit(f"LOAD {self.RIGHT_EXPR}")
            self.emit("JZERO 48")

            # Pętla
            self.emit(f"LOAD {self.RESULT_MODULO}")
            self.emit(f"SUB {self.HELP_B}")     # a - b
            self.emit(f"JPOS {self.RESULT}")    # jeśli a - b >= 0
            self.emit("JZERO 2")   # jeśli a - b = 0
            self.emit("JUMP 8")    

            # Dodajemy b do k i zapisujemy
            self.emit(f"LOAD {self.HELP_B}")
            self.emit(f"ADD {self.HELP_B}")     # b + b_mult
            self.emit(f"STORE {self.HELP_B}")   
            self.emit(f"LOAD {self.HELP}")
            self.emit(f"ADD {self.HELP}")     # k + k
            self.emit(f"STORE {self.HELP}")   
            self.emit("JUMP -11")

            # Zmieniamy wartości pomocnicze (dzielimy przez 2)
            self.emit(f"LOAD {self.HELP}")
            self.emit("HALF")      # k //= 2
            self.emit(f"STORE {self.HELP}")
            self.emit(f"LOAD {self.HELP_B}")
            self.emit("HALF")      # b_mult //= 2
            self.emit(f"STORE {self.HELP_B}") 

            # Sprawdzamy warunki na mod
            self.emit(f"LOAD {self.RESULT_MODULO}")
            self.emit(f"SUB {self.RIGHT_EXPR}")     # a - b
            self.emit(f"JPOS {self.RESULT}")    # jeśli a - b >= 0
            self.emit("JZERO 2")   # jeśli a - b = 0
            self.emit("JUMP 19")   

            # Ponownie obliczamy resztę
            self.emit(f"LOAD {self.RESULT_MODULO}")
            self.emit(f"SUB {self.HELP_B}")     # a - b_mult
            self.emit(f"JPOS {self.RESULT}")    # jeśli a - b_mult >= 0
            self.emit("JZERO 2")   # jeśli a - b_mult = 0
            self.emit("JUMP 7") 

            self.emit(f"LOAD {self.RESULT_MODULO}")    
            self.emit(f"SUB {self.HELP_B}") 
            self.emit(f"STORE {self.RESULT_MODULO}")
            self.emit(f"LOAD {self.RESULT}")

            self.emit(f"ADD {self.HELP}")     # dodaj k do result
            self.emit(f"STORE {self.RESULT}")   
            # Dzielimy ponownie k i b_mult przez 2
            self.emit(f"LOAD {self.HELP}")
            self.emit("HALF")      # k //= 2
            self.emit(f"STORE {self.HELP}") 
            self.emit(f"LOAD {self.HELP_B}")
            self.emit("HALF")      # b_mult //= 2
            self.emit(f"STORE {self.HELP_B}")   

            self.emit("JUMP -22")

            # Sprawdzenie znaku
            self.emit(f"LOAD {self.FLAG_SIGN_LEFT_EXPR}")
            self.emit(f"ADD {self.FLAG_SIGN_RIGHT_EXPR}")
            self.emit("JZERO 10") # jak 0 to skaczemy ten sam znak
            # Zmiana znaku wyniku, jesli różne znaki A i B
            self.emit(f"LOAD {self.RIGHT_EXPR}")
            self.emit(f"SUB {self.RESULT_MODULO}")
            self.emit(f"STORE {self.RESULT_MODULO}")

            self.emit(f"LOAD {self.RESULT}")
            self.emit(f"ADD {self.VALUE_ONE}")
            self.emit(f"STORE {self.RESULT}")
            self.emit("SET 0")
            self.emit(f"SUB {self.RESULT}")
            self.emit(f"STORE {self.RESULT}")

            #Sprawdzenie znaku reszty z dzielenia 
            self.emit(f"LOAD {self.FLAG_SIGN_RIGHT_EXPR}")
            self.emit("JZERO 4")
            # Zmiana znaku reszty, jesli B ujemne
            self.emit("SET 0")
            self.emit(f"SUB {self.RESULT_MODULO}")
            self.emit(f"STORE {self.RESULT_MODULO}")


    def handle_expressionID(self, arg_expression):

        if arg_expression[0] == "UNDECLARED":
            if arg_expression[1] in self.symbol_table.iterators:
                iterator_address, add2 = self.symbol_table.get_iterator(arg_expression[1])
                self.emit(f"LOAD {iterator_address}")
            elif isinstance(self.symbol_table.get_pointer_proc(arg_expression[1]), Variable):
                addr = self.symbol_table.get_pointer_proc(arg_expression[1])
                self.emit(f"LOADI {addr}")
            else:
                raise Exception(f"Undeclared variable '{arg_expression[1]}' on line {arg_expression[2]}.")
        elif arg_expression[0] == "ARRAY":

            array_name, index = arg_expression[1], arg_expression[2]
            address = self.handle_array_index(array_name, index, arg_expression[3], self.ARRAY_POINTER_EXPR)
            
            if address == 0:  
                self.emit(f"LOADI {self.ARRAY_POINTER_EXPR}")  
            else:
                self.emit(f"LOAD {address}") 
        elif isinstance(arg_expression[0], str):
            variable_name = arg_expression
            if variable_name in self.symbol_table:
                address = self.symbol_table.get_pointer(variable_name)
                self.emit(f"LOAD {address}")
            else:      
                raise Exception(f"Unknown variable '{variable_name}' on line {arg_expression[2]}.")
        else:
            raise Exception(f"Invalid expression ID format: '{arg_expression}' on line {arg_expression[2]}.")


    def handle_array_index(self, array_name, index, line, memory_cell):
        if not isinstance(self.symbol_table[array_name], Array):
            raise Exception(f"Using a variable as an array on line {line}.")
        first_index = self.symbol_table[array_name].first_index
        memory_of_first_index = self.symbol_table.get_pointer([array_name, first_index])
        array_offset = memory_of_first_index - first_index
        address = 0
        if isinstance(index, int):  
            address = self.symbol_table.get_pointer([array_name, index])
        elif isinstance(index, tuple) and index[0] == "ID":
            
            if isinstance(index[1], tuple) and index[1][0] == "UNDECLARED":
                if index[1][1] in self.symbol_table.iterators:
                    iterator_address, add2 = self.symbol_table.get_iterator(index[1][1])
                    self.emit(f"SET {array_offset}")
                    self.emit(f"ADD {iterator_address}")
                    self.emit(f"STORE {memory_cell}")
                    #TODO: sprawdzić, czy nie wyszło za zakres
                elif self.symbol_table.current_procedure:
                    if index[1][1] in self.symbol_table.procedures[self.symbol_table.current_procedure].local_variables:
                        variable_address = self.symbol_table.procedures[self.symbol_table.current_procedure].local_variables[index[1][1]]
                        self.emit(f"SET {array_offset}")
                        self.emit(f"ADD {variable_address}")
                        self.emit(f"STORE {memory_cell}")

                    elif index[1][1] in self.symbol_table:
                        variable_address = self.symbol_table.get_pointer(index[1][1])
                        self.emit(f"SET {array_offset}")
                        self.emit(f"ADD {variable_address}")
                        self.emit(f"STORE {memory_cell}")
                    else:
                        raise Exception(f"Undeclared index variable '{index[1][1]}' on line {line}.")
                else:
                    raise Exception(f"Undeclared index variable '{index[1][1]}' on line {line}.")
                
            elif isinstance(index[1], str): 
                variable_address = self.symbol_table.get_pointer(index[1])
                if not self.symbol_table[index[1]].initialized:
                    raise Exception(f"Index variable '{index[1]}' is not initialized on line {line}.")
                self.emit(f"SET {array_offset}")
                self.emit(f"ADD {variable_address}")
                self.emit(f"STORE {memory_cell}")
                #TODO: sprawdzić, czy nie wyszło za zakres
            else:
                raise Exception(f"Invalid index type '{index}' on line {line}.")
        else:
            raise Exception(f"Unsupported index format '{index}' on line {line}.")
        
        return address