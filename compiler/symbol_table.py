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

class SymbolTable(dict):
    def __init__(self):
        super().__init__()
        self.memory_counter = 0
        self.iterators = {}

    def add_variable(self, name):
        if name in self:
            raise ValueError(f"ERROR: variable '{name}' already declared.")
        self[name] = Variable(self.memory_counter) #self.setdefault(name, Variable(self.memory_counter)) żeby nie nadpisywało? ale czy nadpisuje? idk
        self.memory_counter += 1

    def add_array(self, name, first_index, last_index):
        if name in self:
            raise ValueError(f"ERROR: array '{name}' already declared.")
        elif first_index > last_index:
            raise Exception(f"ERROR: first_index > last_index at array {name}.")
        array_size = last_index - first_index + 1
        self[name] = Array(first_index, last_index, self.memory_counter) #self.setdefault(name, Array(name, self.memory_counter, first_index, last_index))
        self.memory_counter += array_size

    def add_iterator(self, name):
        if name in self:
            raise ValueError(f"Iterator '{name}' already declared.")
        iterator = Iterator(self.memory_counter + 1, self.memory_counter) #
        self[name] = iterator #self.iterators.setdefault(name, Iter(self.memory_counter + 1, self.memory_counter))
        self.memory_counter += 2

    def get_variable(self, name):
        if name in self:
            return self[name]
        elif name in self.iterators:
            return self.iterators[name]
        else:
            raise ValueError(f"ERROR: unknow variable {name}.")

    def get_array_at(self, name, index):
        if name in self:
            try:
                return self[name].get_memory_index(index)
            except:
                raise Exception(f"ERROR: non-array {name} used as an array.")
        else:
            raise ValueError(f"ERROR: undeclared array {name}.")  
        
    def get_iterator(self, name):
        if name in self:
            iterator = self[name]
            return iterator.base_memory_index, iterator.times
        else:
            raise ValueError(f"ERROR: undeclared iterator {name}.")
        
    def get_pointer(self, name):
        if type(name) == str:
            return self.get_variable(name).memory_counter
        else:
            return self.get_array(name[0], name[1])


symbol_table = SymbolTable()

symbol_table.add_variable("x")
symbol_table.add_variable("y")
symbol_table.add_array("arr", -10, 10)
symbol_table.add_iterator("i")

print("Variable x memory index:", symbol_table.get_variable("x"))
print("Variable y memory index:", symbol_table.get_variable("y"))
print("Array arr[0] memory index:", symbol_table.get_array_at("arr", 0))
print("Iterator i memory index:", symbol_table.get_iterator("i"))

