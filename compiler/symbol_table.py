class Variable:
    def __init__(self, base_memory_index, is_local=False, is_parameter=False):
        self.base_memory_index = base_memory_index
        self.is_local = is_local  # Zmienna lokalna w procedurze
        self.is_parameter = is_parameter  # Parametr formalny procedury
        self.initialized = False

    def __repr__(self):
        return str(self.base_memory_index)

class Iterator:
    def __init__(self, base_memory_index, limit_memory):
        self.base_memory_index = base_memory_index
        self.limit_memory = limit_memory

    def __repr__(self):
        return str(self.base_memory_index)

class Array:
    def __init__(self, first_index, last_index, base_memory_index):
        #self.name = name
        self.first_index = first_index
        self.last_index = last_index
        self.base_memory_index = base_memory_index

    def get_memory_index(self, index):
        if index < self.first_index or index > self.last_index:
            raise IndexError("Array index out of bounds.")
        return self.base_memory_index + (index - self.first_index)

    def __repr__(self):
        return str(self.base_memory_index)
    
class Procedure:
    def __init__(self, name, base_memory_index, params, local_variables, commands):
        self.name = name
        self.base_memory_index = base_memory_index
        self.params = params
        self.local_variables = local_variables
        self.commands = commands

    def __repr__(self):
        return f"{self.name}, {self.base_memory_index}, {self.params}, {self.local_variables}, {self.commands}"

    #Mapowanie????
    def bind_parameters(self, args):
        if len(args) != len(self.params):
            raise ValueError(f"Incorrect number of arguments for procedure {self.name}.")
        return {param: args[i] for i, param in enumerate(self.params)}

class SymbolTable(dict):
    def __init__(self):
        super().__init__()
        self.memory_counter = 20
        self.iterators = {}
        self.procedures = {}
        self.constants = {}
        self.current_procedure = None 

    def add_variable(self, name):
        if self.current_procedure:
            procedure = self.procedures[self.current_procedure]
            
            # Jeśli zmienna już istnieje jako lokalna, błąd
            if name in procedure.local_variables:
                raise ValueError(f"Local variable '{name}' already declared in procedure {self.current_procedure}.")
            
            # Dodajemy zmienną lokalną do procedury
            procedure.local_variables[name] = Variable(self.memory_counter, is_local=True)
        
        else:
            # Jeśli jesteśmy poza procedurą (np. w MAIN), dodajemy do globalnego zakresu
            if name in self:
                raise ValueError(f"Variable '{name}' already declared globally.")
            self[name] = Variable(self.memory_counter)

        self.memory_counter += 1  # Zwiększamy licznik pamięci


    def add_array(self, name, first_index, last_index):
        if name in self:
            raise ValueError(f"Array '{name}' already declared.")
        elif first_index > last_index:
            raise IndexError(f"First_index > last_index at array '{name}'.")
        array_size = last_index - first_index + 1
        self[name] = Array(first_index, last_index, self.memory_counter)
        self.memory_counter += array_size

    def add_iterator(self, name):
        limit_memory = self.memory_counter
        iterator = Iterator(self.memory_counter + 1, limit_memory) 
        self.iterators[name] = iterator
        self.memory_counter += 2
        return self.memory_counter - 1, limit_memory
    
    def is_iterator(self, value):
        return value in self.iterators
    
    def add_procedure(self, name, params, local_variables, commands):
        if name in self.procedures:
            raise ValueError(f"Redeclaration of procedure '{name}'.")
        if name in self:
            raise Exception(f"Overloading name of the procedure {name}.")

        self.current_procedure = name

        # Przydzielamy miejsce na parametry (wskaźniki na argumenty)
        param_memory = {}
        for param in params:
            
            param_memory[param] = Variable(self.memory_counter, is_parameter=True)
            print(param_memory[param])
            self.memory_counter += 1  # Każdy parametr dostaje jedno miejsce na wskaźnik

        # Przydzielamy miejsce na zmienne lokalne
        local_memory = {}
        for var in local_variables:
            local_memory[var] = Variable(self.memory_counter, is_local=True)
            print(local_memory[var])
            self.memory_counter += 1
        print(param_memory, local_memory)
        # Tworzymy obiekt procedury
        self.procedures[name] = Procedure(name, self.memory_counter, param_memory, local_memory, commands)
        
        self.validate_procedure(name)
        self.current_procedure = None  # Reset po zakończeniu

    
    def validate_procedure(self, name):
        _, _, _, _, commands = self.get_procedure(name)

        for command in commands:
            if command[0] == "PROC_CALL":
                called_proc = command[1]
                if called_proc not in self.procedures:
                    raise Exception(f"Procedure {called_proc} called in {name} is not defined")
                if list(self.procedures.keys()).index(called_proc) > list(self.procedures.keys()).index(name):
                    raise Exception(f"Procedure {called_proc} must be defined before it is called in {name}")

            
    def get_procedure(self, name):
        if name in self.procedures:
            procedure = self.procedures[name]
            return procedure.name, procedure.base_memory_index, procedure.params, procedure.local_variables, procedure.commands
        else:
            raise ValueError(f"Undeclared procedure '{name}'.")
        
        
    def add_const(self, value):
        if value in self.constants:
            return self.constants[value]
        self.constants[value] = self.memory_counter
        self.memory_counter += 1
        return self.memory_counter - 1

    def get_variable(self, name):  
        if name in self:
            return self[name]
        elif name in self.iterators:
            return self.iterators[name]
        else:
            raise ValueError(f"Unknow variable '{name}'.")

    def get_array_at(self, name, index):
        if name in self:
            try:
                return self[name].get_memory_index(index)
            except:
                raise Exception(f"Non-array '{name}' used as an array.")
        else:
            raise ValueError(f"Undeclared array '{name}'.")  
        
    def get_iterator(self, name):
        if name in self.iterators:
            iterator = self.iterators[name]
            return iterator.base_memory_index, iterator.limit_memory
        else:
            raise ValueError(f"Undeclared iterator '{name}'.")

    def get_pointer_proc(self, name):
        if self.current_procedure:
            procedure = self.procedures[self.current_procedure]
            if name in procedure.params:
                return procedure.params[name]  # Parametr przechowuje wskaźnik na argument
            elif name in procedure.local_variables:
                return procedure.local_variables[name]  # Normalna zmienna lokalna
            
    def get_pointer(self, name):
        

        if type(name) == str:
            return self.get_variable(name).base_memory_index
        else:
            return self.get_array_at(name[0], name[1])
        
    def get_const(self, value):
        if value in self.constants:
            return self.constants[value]
        else:
            raise ValueError(f"Constant value '{value}' not found.")
        
    def remove_variable(self, name):
        if name in self:
            del self[name]
        else:
            raise ValueError(f"Variable '{name}' not found.")
        