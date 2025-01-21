class CodeGenerator:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.code = []
        self.label_counter = 0
        self.constants = {}

    def generate_label(self):
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label

    def emit(self, instruction):
        self.code.append(instruction)

    def generate(self, ast):
        if ast[0] == "PROGRAM":
            _, procedures, main = ast
            self.generate_procedures(procedures)
            self.generate_main(main)
        return "\n".join(self.code)
    
    # procedury PÓŹNIEJ
    def generate_procedures(self, procedures):
        for procedure in procedures:
            _, name, declarations, commands = procedure
            self.emit(f"{name}:")
            self.generate_commands(commands)
            self.emit("RTRN p0") # ???????

    # main
    def generate_main(self, main):
        if main[0] == "MAIN_DEC":
            _, declarations, commands = main # obsłużyć declarations
            self.generate_commands(commands)
        elif main[0] == "MAIN":
            _, commands = main
            self.generate_commands(commands)
        self.emit("HALT")

    def generate_commands(self, commands):
        for command in commands:
            self.generate_command(command)
            

    def generate_command(self, command):
        match command:
            case ("ASSIGN", var, expression):
                pass
            case ("WRITE", value):
                pass
            case ("READ", var):
                pass
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

    def generate_condition(self, condition):
        op, left, right = condition
        match op:
            case "EQUAL":
                pass
            case "NEQUAL":
                pass
            case "GREATER":
                pass
            case "LESS":
                pass
            case "GEQ":
                pass
            case "LEQ":
                pass

    def generate_expression(self, expression):
        op, left, right = expression

        match op:
            case "PLUS":
                pass
            case "MINUS":
                pass
            case "MULTIPLY":
                pass
            case "DIVIDE":
                pass
            case "MOD":
                pass
