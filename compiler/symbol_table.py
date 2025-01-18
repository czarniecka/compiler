class Variable:
    def __init__(self, base_memory_index):
        self.base_memory_index = base_memory_index
        self.initialized = False

    def __repr__(self):
        return str(self.base_memory_index)

class Iterator:
    def __init__(self, base_memory_index, times):
        self.base_memory_index = base_memory_index
        self.times = times

    def __repr__(self):
        return str(self.base_memory_index)

class Array:
    def __init__(self, first_index, last_index, base_memory_index):
        if first_index > last_index:
            raise ValueError("ERROR: first_index index greater than last_index index.")
        #self.name = name
        self.first_index = first_index
        self.last_index = last_index
        self.base_memory_index = base_memory_index

    def get_memory_index(self, index):
        if index < self.first_index or index > self.last_index:
            raise IndexError("ERROR: array index out of bounds.")
        return self.base_memory_index + (index - self.first_index)

    def __repr__(self):
        return str(self.base_memory_index)
    
class Procedure:
    def __init__(self, name, base_memory_index, params, local_variables, commands):
        self.name = name
        self.base_memory_index = base_memory_index
        self.params = {param: base_memory_index + i for i, param in enumerate(params)}
        self.local_variables = {variables: base_memory_index + len(params) + i for i, variables in enumerate(local_variables)}  
        self.commands = commands

    def __repr__(self):
        return f"Procedure({self.name} at {self.base_memory_index} (params={self.params}, local_variables={self.local_variables})"
    
    #Mapowanie????
    def bind_parameters(self, args):
        if len(args) != len(self.params):
            raise ValueError(f"ERROR: incorrect number of arguments for procedure {self.name}.")
        return dict(zip(self.params, args))

class SymbolTable(dict):
    def __init__(self):
        super().__init__()
        self.memory_counter = 0
        self.iterators = {}
        self.procedures = {}

    def add_variable(self, name):
        if name in self:
            raise ValueError(f"ERROR: variable '{name}' already declared.")
        self[name] = Variable(self.memory_counter) #self.setdefault(name, Variable(self.memory_counter)) żeby nie nadpisywało? ale czy nadpisuje? idk
        self.memory_counter += 1

    def add_array(self, name, first_index, last_index):
        if name in self:
            raise ValueError(f"ERROR: array '{name}' already declared.")
        elif first_index > last_index:
            raise IndexError(f"ERROR: first_index > last_index at array '{name}'.")
        array_size = last_index - first_index + 1
        self[name] = Array(first_index, last_index, self.memory_counter) #self.setdefault(name, Array(name, self.memory_counter, first_index, last_index))
        self.memory_counter += array_size

    def add_iterator(self, name):
        if name in self:
            raise ValueError(f"Iterator '{name}' already declared.")
        iterator = Iterator(self.memory_counter + 1, self.memory_counter) #
        self.iterators[name] = iterator #self.iterators.setdefault(name, Iter(self.memory_counter + 1, self.memory_counter))
        self.memory_counter += 2

    def add_procedure(self, name, params, local_variables, command):
        if name in self.procedures:
            raise ValueError(f"ERROR: redeclaration of procedure '{name}'.")
        self.procedures[name] = Procedure(name, self.memory_counter, params, local_variables, command)
        self.memory_counter += len(params) + len(local_variables)

    def get_variable(self, name):
        if name in self:
            return self[name]
        elif name in self.iterators:
            return self.iterators[name]
        else:
            raise ValueError(f"ERROR: unknow variable '{name}'.")

    def get_array_at(self, name, index):
        if name in self:
            try:
                return self[name].get_memory_index(index)
            except:
                raise Exception(f"ERROR: non-array '{name}' used as an array.")
        else:
            raise ValueError(f"ERROR: undeclared array '{name}'.")  
        
    def get_iterator(self, name):
        if name in self.iterators:
            return self.iterators[name]
        else:
            raise ValueError(f"ERROR: undeclared iterator '{name}'.")
        
    def get_procedure(self, name):
        if name in self.procedures:
            return self.procedures[name]
        else:
            raise ValueError(f"ERROR: undeclared procedure '{name}'.")
        
    def get_pointer(self, name):
        if type(name) == str:
            return self.get_variable(name).memory_counter
        else:
            return self.get_array_at(name[0], name[1])


symbol_table = SymbolTable()

symbol_table.add_variable("x")
symbol_table.add_variable("y")
print(symbol_table)

symbol_table.add_array("arr", -10, 10)
symbol_table.add_array("matrix", 0, 1)
print(symbol_table)

symbol_table.add_iterator("i")
symbol_table.add_iterator("j")
print(symbol_table)

print("iterators:", symbol_table.iterators)

params = ["param1", "param2"]
local_variables = ["local1", "local2"]
commands = ["command1", "command2"]  # Placeholder for commands

symbol_table.add_procedure("myProcedure", params, local_variables, commands)
symbol_table.add_procedure(
        "najlepszatablica",
        [("a", "ble")],
        [("WKS", "hejslask")],
        [("bober", "array")]
    )
print(symbol_table)   
print("procedures:", symbol_table.procedures)

print(f"Adres arr[-5]: {symbol_table.get_array_at('arr', -4)}")
print(f"Adres matrix[2]: {symbol_table.get_array_at('matrix', 1)}")
print("Variable x memory index:", symbol_table.get_variable("x"))
print("Variable y memory index:", symbol_table.get_variable("y"))
print("Array arr[0] memory index:", symbol_table.get_array_at("arr", 0))
print("Iterator i memory index:", symbol_table.get_iterator("i"))
print("Procedure 'myProcedure':", symbol_table.get_procedure("myProcedure"))
print(f"Procedura 'foo': {symbol_table.get_procedure('najlepszatablica')}")

print("Obsługa błędów -------------------------")

try:
    symbol_table.add_variable("x")  
except Exception as e:
    print(f"{e}")

try:
    symbol_table.get_array_at("matrix", 10)  
except Exception as e:
    print(f"{e}")

try:
    symbol_table.get_variable("hehe") 
except Exception as e:
    print(f"{e}")
