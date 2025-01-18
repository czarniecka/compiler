from sly import Parser
from lexer import my_lexer
from symbol_table import SymbolTable, Variable, Iterator, Array

class my_parser(Parser):

    tokens = my_lexer.tokens
    symbol_table = SymbolTable()

    literal_constants = set()

    precedence = (
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MULTIPLY', 'DIVIDE', 'MOD')
    )

    # program_all
    @_('procedures main')
    def program_all(self, p):
        pass
    
    # procedures
    @_('procedures PROCEDURE proc_head IS declarations BEGIN commands END')
    def procedures(self, p):
        pass
    @_('procedures PROCEDURE proc_head IS BEGIN commands END')
    def procedures(self, p):
        pass
    @_('')
    def procedures(self, p):
        return []
    
    # main
    @_('PROGRAM IS declarations BEGIN commands END')
    def main(self, p):
        pass
    @_('PROGRAM IS BEGIN commands END')
    def main(self, p):
        pass

    # commands
    @_('commands command')
    def commands(self, p):
        return p[0] + [p[1]]
    @_('command')
    def commands(self, p):
        return [p[0]]

    # command
    @_('identifier ASSIGN expression SEMICOLON')
    def command(self, p):
        return "ASSIGN", p[0], p[2]

    @_('IF condition THEN commands ELSE commands ENDIF')
    def command(self, p):
        if_else_com = "IFELSE", p[1], p[3], p[5], self.literal_constants.copy()
        self.literal_constants.clear()
        return if_else_com
    
    @_('IF condition THEN commands ENDIF')
    def command(self, p):
        if_com = "IF", p[1], p[3], self.literal_constants.copy()
        self.literal_constants.clear()
        return if_com
    
    @_('WHILE condition DO commands ENDWHILE')
    def command(self, p):
        while_com = "WHILE", p[1], p[3], self.literal_constants.copy()
        self.literal_constants.clear()
        return while_com
    
    @_('REPEAT commands UNTIL condition SEMICOLON')
    def command(self, p):
        repeat_com = "REPEAT", p[3], p[1], self.literal_constants.copy()
        self.literal_constants.clear()
        return repeat_com
    
    @_('FOR PIDENTIFIER FROM value TO value DO commands ENDFOR')  
    def command(self, p):
        for_to_com = "FORTO", p[1], p[3], p[5], p[7], self.literal_constants.copy()
        self.literal_constants.clear()
        return for_to_com
     
    @_('FOR PIDENTIFIER FROM value DOWNTO value DO commands ENDFOR')   
    def command(self, p):
        for_downto_com = "FORDOWNTO", p[1], p[3], p[5], p[7], self.literal_constants.copy()
        self.literal_constants.clear()
        return for_downto_com
     
    @_('proc_call SEMICOLON')
    def command(self, p):
        pass

    @_('READ identifier SEMICOLON')
    def command(self, p):
        return "READ", p[1]
    
    @_('WRITE value SEMICOLON')
    def command(self, p):
        if p[1][0] == "NUM":
            self.literal_constants.add(int(p[1][1]))
        return "WRITE", p[1]

    # proc_head
    @_('PIDENTIFIER LPAREN args_decl RPAREN')
    def proc_head(self, p):
        pass

    # proc_call
    @_('PIDENTIFIER LPAREN args RPAREN')
    def proc_call(self, p):
        pass

    # declarations 
    @_('declarations COMMA PIDENTIFIER')
    def declarations(self, p):
        pass
    @_('declarations COMMA PIDENTIFIER LBRACKET NUM COLON NUM RBRACKET')
    def declarations(self, p):
        pass
    @_('PIDENTIFIER')
    def declarations(self, p):
        pass
    @_('PIDENTIFIER LBRACKET NUM COLON NUM RBRACKET')
    def declarations(self, p):
        pass

    # args_decl
    @_('args_decl COMMA PIDENTIFIER')
    def args_decl(self, p):
        pass
    @_('args_decl COMMA T PIDENTIFIER')
    def args_decl(self, p):
        pass
    @_('PIDENTIFIER')
    def args_decl(self, p):
        pass
    @_('T PIDENTIFIER')
    def args_decl(self, p):
        pass

    # args
    @_('args COMMA PIDENTIFIER')
    def args(self, p):
        pass
    @_('PIDENTIFIER')
    def args(self, p):
        pass

    # expression
    @_('value')
    def expression(self, p):
        return p[0]
    
    @_('value PLUS value')
    def expression(self, p):
        return "PLUS", p[0], p[2]
    
    @_('value MINUS value')
    def expression(self, p):
        return "MINUS", p[0], p[2]
    
    @_('value MULTIPLY value')
    def expression(self, p):
        return "MULTIPLY", p[0], p[2]
    
    @_('value DIVIDE value')
    def expression(self, p):
        return "DIVIDE", p[0], p[2]
    
    @_('value MOD value')
    def expression(self, p):
        return "MOD", p[0], p[2]

    # condition 
    @_('value EQUAL value')
    def condition(self, p):
        return "EQUAL", p[0], p[2]
    
    @_('value NEQUAL value')
    def condition(self, p):
        return "NEQUAL", p[0], p[2]
    
    @_('value GREATER value')
    def condition(self, p):
        return "GREATER", p[0], p[2]
    
    @_('value LESS value')
    def condition(self, p):
        return "LESS", p[0], p[2]
    
    @_('value GEQ value')
    def condition(self, p):
        return "GEQ", p[0], p[2]
    
    @_('value LEQ value')
    def condition(self, p):
        return "LEQ", p[0], p[2]

    # value
    @_('NUM')
    def value(self, p):
        return "NUM", p[0]
    
    @_('identifier')
    def value(self, p):
        return "ID", p[0]

    # identifier
    @_('PIDENTIFIER')
    def identifier(self, p):
        if p[0] in self.symbol_table or p[0] in self.symbol_table.iterators:
            return p[0]
        else:
            return "UNDECLARED", p[0]
        
    @_('PIDENTIFIER LBRACKET PIDENTIFIER RBRACKET')
    def identifier(self, p):
        pass
        
    @_('PIDENTIFIER LBRACKET NUM RBRACKET')
    def identifier(self, p):
        pass

    # -----------------------------------------------
    def error(self, p):
        if p:
            print(f'Syntax error: {p.type}')
        else:
            print("Syntax error at EOF")