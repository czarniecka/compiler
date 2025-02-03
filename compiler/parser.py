from sly import Parser
from lexer import my_lexer
from symbol_table import SymbolTable, Variable, Array
from code_generator import CodeGenerator

class my_parser(Parser):

    tokens = my_lexer.tokens
    symbol_table = SymbolTable()

    def __init__(self):
        super().__init__()
        self.generator = CodeGenerator(self.symbol_table)

    literal_constants = set()

    precedence = (
        ('left', 'PLUS', 'MINUS'), 
        ('left', 'MULTIPLY', 'DIVIDE', 'MOD') 
    )


    # program_all: program składa się z procedur (opcjonalne) i głównego programu main
    @_('procedures main') # type: ignore
    def program_all(self, p):
        ast = ("PROGRAM", p.procedures, p.main)
        asm_code = self.generator.generate(ast)
        return asm_code


    # procedures
    @_('procedures PROCEDURE proc_head IS declarations BEGIN commands END') # type: ignore
    def procedures(self, p):
        return p[0] + [("PROCEDURE", p[2], p[4], p[6])]

    @_('procedures PROCEDURE proc_head IS BEGIN commands END') # type: ignore
    def procedures(self, p):
        return p[0] + [("PROCEDURE", p[2], [], p[5])]

    @_('') # type: ignore
    def procedures(self, p):
        return []


    # main
    @_('PROGRAM IS declarations BEGIN commands END') # type: ignore
    def main(self, p):
        return "MAIN_DEC", p[2], p[4]

    @_('PROGRAM IS BEGIN commands END') # type: ignore
    def main(self, p):
        return "MAIN", p[3]


    # commands
    @_('commands command') # type: ignore
    def commands(self, p):
        return p[0] + [p[1]]

    @_('command') # type: ignore
    def commands(self, p):
        return [p[0]]


    # command
    @_('identifier ASSIGN expression SEMICOLON') # type: ignore
    def command(self, p):
        return "ASSIGN", p[0], p[2]

    @_('IF condition THEN commands ELSE commands ENDIF') # type: ignore
    def command(self, p):
        if_else_com = "IFELSE", p[1], p[3], p[5], self.literal_constants.copy()
        self.literal_constants.clear()
        return if_else_com

    @_('IF condition THEN commands ENDIF') # type: ignore
    def command(self, p):
        if_com = "IF", p[1], p[3], self.literal_constants.copy()
        self.literal_constants.clear()
        return if_com

    @_('WHILE condition DO commands ENDWHILE') # type: ignore
    def command(self, p):
        while_com = "WHILE", p[1], p[3], self.literal_constants.copy()
        self.literal_constants.clear()
        return while_com

    @_('REPEAT commands UNTIL condition SEMICOLON') # type: ignore
    def command(self, p):
        repeat_com = "REPEAT", p[1], p[3], self.literal_constants.copy()
        self.literal_constants.clear()
        return repeat_com

    @_('FOR PIDENTIFIER FROM value TO value DO commands ENDFOR')  # type: ignore
    def command(self, p):
        for_to_com = "FORTO", p[1], p[3], p[5], p[7], self.literal_constants.copy()
        self.literal_constants.clear()
        return for_to_com

    @_('FOR PIDENTIFIER FROM value DOWNTO value DO commands ENDFOR')   # type: ignore
    def command(self, p):
        for_downto_com = "FORDOWNTO", p[1], p[3], p[5], p[7], self.literal_constants.copy()
        self.literal_constants.clear()
        return for_downto_com

    @_('proc_call SEMICOLON') # type: ignore
    def command(self, p):
        return p[0]

    @_('READ identifier SEMICOLON') # type: ignore
    def command(self, p):
        return "READ", p[1]

    @_('WRITE value SEMICOLON') # type: ignore
    def command(self, p):
        if p[1][0] == "NUM":
            self.symbol_table.add_const(p[1][1])
        return "WRITE", p[1]


    # proc_head
    @_('PIDENTIFIER LPAREN args_decl RPAREN') # type: ignore
    def proc_head(self, p):
        return p[0], p[2]


    # proc_call
    @_('PIDENTIFIER LPAREN args RPAREN') # type: ignore
    def proc_call(self, p):
        if(p[2][0] == "sito"):
            p[2][0] = p[2][0][0]
        return "PROC_CALL", p[0], p[2], p.lineno


    # declarations
    @_('declarations COMMA PIDENTIFIER') # type: ignore
    def declarations(self, p):
        self.symbol_table.add_variable(p[2])
        return p[0] + [("VAR", p[2])]

    @_('declarations COMMA PIDENTIFIER LBRACKET number COLON number RBRACKET') # type: ignore
    def declarations(self, p):
        if(p[2] == "sito"):
            p[2] = p[2][0]
        self.symbol_table.add_array(p[2], p[4], p[6], p.lineno)
        return p[0] + [("ARRAY", p[2], p[4], p[6])]

    @_('PIDENTIFIER') # type: ignore
    def declarations(self, p):
        self.symbol_table.add_variable(p[0])
        return [("VAR", p[0])]

    @_('PIDENTIFIER LBRACKET number COLON number RBRACKET') # type: ignore
    def declarations(self, p):
        self.symbol_table.add_array(p[0], p[2], p[4], p.lineno)
        return [("ARRAY", p[0], p[2], p[4])]


    # args_decl
    @_('args_decl COMMA PIDENTIFIER') # type: ignore
    def args_decl(self, p):
        return p[0] + [p[2]]

    @_('args_decl COMMA T PIDENTIFIER') # type: ignore
    def args_decl(self, p):
        return p[0] + [(p[2], p[3])]

    @_('PIDENTIFIER') # type: ignore
    def args_decl(self, p):
        return [p[0]]

    @_('T PIDENTIFIER') # type: ignore
    def args_decl(self, p):
        return [(p[0], p[1])]


    # args
    @_('args COMMA PIDENTIFIER') # type: ignore
    def args(self, p):
        return p[0] + [p[2]]

    @_('PIDENTIFIER') # type: ignore
    def args(self, p):
        return [p[0]]


    # expression
    @_('value') # type: ignore
    def expression(self, p):
        return p[0]

    @_('value PLUS value') # type: ignore
    def expression(self, p):
        return "PLUS", p[0], p[2]

    @_('value MINUS value') # type: ignore
    def expression(self, p):
        return "MINUS", p[0], p[2]

    @_('value MULTIPLY value') # type: ignore
    def expression(self, p):
        return "MULTIPLY", p[0], p[2]

    @_('value DIVIDE value') # type: ignore
    def expression(self, p):
        return "DIVIDE", p[0], p[2]

    @_('value MOD value') # type: ignore
    def expression(self, p):
        return "MOD", p[0], p[2]


    # condition 
    @_('value EQUAL value') # type: ignore
    def condition(self, p):
        return "EQUAL", p[0], p[2]

    @_('value NEQUAL value') # type: ignore
    def condition(self, p):
        return "NEQUAL", p[0], p[2]

    @_('value GREATER value') # type: ignore
    def condition(self, p):
        return "GREATER", p[0], p[2]

    @_('value LESS value') # type: ignore
    def condition(self, p):
        return "LESS", p[0], p[2]

    @_('value GEQ value') # type: ignore
    def condition(self, p):
        return "GEQ", p[0], p[2]

    @_('value LEQ value') # type: ignore
    def condition(self, p):
        return "LEQ", p[0], p[2]


    # number
    @_('NUM') # type: ignore
    def number(self, p):
        return p[0]
    
    @_('MINUS NUM') # type: ignore
    def number(self, p):
        return -(p[1])
    

    # value
    @_('number')
    def value(self, p):
        return "NUM", p[0]

    @_('identifier') # type: ignore
    def value(self, p):
        return "ID", p[0]


    # identifier
    @_('PIDENTIFIER') # type: ignore
    def identifier(self, p):
        if p[0] in self.symbol_table or p[0] in self.symbol_table.iterators:
            return p[0]
        else:
            return "UNDECLARED", p[0], p.lineno

    @_('PIDENTIFIER LBRACKET PIDENTIFIER RBRACKET') # type: ignore
    def identifier(self, p):
        if p[0] in self.symbol_table and type(self.symbol_table[p[0]]) == Array:
            if p[2] in self.symbol_table and type(self.symbol_table[p[2]]) == Variable:
                return "ARRAY", p[0], ("ID", p[2]), p.lineno
            else:
                return "ARRAY", p[0], ("ID", ("UNDECLARED", p[2])), p.lineno
        else:
            if p[2] in self.symbol_table and type(self.symbol_table[p[2]]) == Variable:
                return "ARRAY", p[0], ("ID", p[2]), p.lineno
            else:
                return "ARRAY", p[0], ("ID", ("UNDECLARED", p[2])), p.lineno

    @_('PIDENTIFIER LBRACKET number RBRACKET') # type: ignore
    def identifier(self, p):
        if p[0] in self.symbol_table and type(self.symbol_table[p[0]]) == Array:
            return "ARRAY", p[0], p[2], p.lineno
        else:
            return "ARRAY", p[0], p[2], p.lineno


    # errors
    def error(self, p):
        if p:
            print(f'Syntax error: {p.type} on line {p.lineno}.')
        else:
            print("Syntax error at EOF.")
