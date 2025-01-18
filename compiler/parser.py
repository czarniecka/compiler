from sly import Parser
from lexer import my_lexer

class my_parser(Parser):

    tokens = my_lexer.tokens
    start = 'program_all'

    precedence = (
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MULTIPLY', 'DIVIDE', 'MOD')
    )

    # program_all
    @_('procedures main')
    def program_all(self, t):
        pass
    
    # procedures
    @_('procedures PROCEDURE proc_head IS declarations BEGIN commands END')
    def procedures(self, t):
        pass
    @_('procedures PROCEDURE proc_head IS BEGIN commands END')
    def procedures(self, t):
        pass
    @_('')
    def procedures(self, t):
        pass
    
    # main
    @_('PROGRAM IS declarations BEGIN commands END')
    def main(self, t):
        pass
    @_('PROGRAM IS BEGIN commands END')
    def main(self, t):
        pass

    # commands
    @_('commands command')
    def commands(self, t):
        pass
    @_('command')
    def commands(self, t):
        pass

    # command
    @_('identifier ASSIGN expression SEMICOLON')
    def command(self, t):
        # Załaduj wynik wyrażenia do akumulatora
        self.code_gen.emit("LOAD " + t.expression)
        # Zapisz wynik do zmiennej
        self.code_gen.emit("STORE " + t.identifier)
        
    @_('IF condition THEN commands ELSE commands ENDIF')
    def command(self, t):
        pass
    @_('IF condition THEN commands ENDIF')
    def command(self, t):
        pass
    @_('WHILE condition DO commands ENDWHILE')
    def command(self, t):
        pass
    @_('REPEAT commands UNTIL condition SEMICOLON')
    def command(self, t):
        pass
    @_('FOR PIDENTIFIER FROM value TO value DO commands ENDFOR')  
    def command(self, t):
        pass  
    @_('FOR PIDENTIFIER FROM value DOWNTO value DO commands ENDFOR')   
    def command(self, t):
        pass  
    @_('proc_call SEMICOLON')
    def command(self, t):
        pass
    @_('READ identifier SEMICOLON')
    def command(self, t):
        pass
    @_('WRITE value SEMICOLON')
    def command(self, t):
        pass

    # proc_head
    @_('PIDENTIFIER LPAREN args_decl RPAREN')
    def proc_head(self, t):
        pass

    # proc_call
    @_('PIDENTIFIER LPAREN args RPAREN')
    def proc_call(self, t):
        pass

    # declarations 
    @_('declarations COMMA PIDENTIFIER')
    def declarations(self, t):
        pass
    @_('declarations COMMA PIDENTIFIER LBRACKET NUM COLON NUM RBRACKET')
    def declarations(self, t):
        pass
    @_('PIDENTIFIER')
    def declarations(self, t):
        pass
    @_('PIDENTIFIER LBRACKET NUM COLON NUM RBRACKET')
    def declarations(self, t):
        pass

    # args_decl
    @_('args_decl COMMA PIDENTIFIER')
    def args_decl(self, t):
        pass
    @_('args_decl COMMA T PIDENTIFIER')
    def args_decl(self, t):
        pass
    @_('PIDENTIFIER')
    def args_decl(self, t):
        pass
    @_('T PIDENTIFIER')
    def args_decl(self, t):
        pass

    # args
    @_('args COMMA PIDENTIFIER')
    def args(self, t):
        pass
    @_('PIDENTIFIER')
    def args(self, t):
        pass

    # expression
    @_('value')
    def expression(self, t):
        pass
    @_('value PLUS value')
    def expression(self, t):
        pass
    @_('value MINUS value')
    def expression(self, t):
        pass
    @_('value MULTIPLY value')
    def expression(self, t):
        pass
    @_('value DIVIDE value')
    def expression(self, t):
        pass
    @_('value MOD value')
    def expression(self, t):
        pass

    # condition 
    @_('value EQUAL value')
    def condition(self, t):
        pass
    @_('value NEQUAL value')
    def condition(self, t):
        pass
    @_('value GREATER value')
    def condition(self, t):
        pass
    @_('value LESS value')
    def condition(self, t):
        pass
    @_('value GEQ value')
    def condition(self, t):
        pass
    @_('value LEQ value')
    def condition(self, t):
        pass

    # value
    @_('NUM')
    def value(self, t):
        pass
    @_('identifier')
    def value(self, t):
        pass

    # identifier
    @_('PIDENTIFIER')
    def identifier(self, t):
        pass
    @_('PIDENTIFIER LBRACKET PIDENTIFIER RBRACKET')
    def identifier(self, t):
        pass
    @_('PIDENTIFIER LBRACKET NUM RBRACKET')
    def identifier(self, t):
        pass

    # -----------------------------------------------
    def error(self, t):
        if p:
            print(f'Syntax error: {t.type}')
        else:
            print("Syntax error at EOF")