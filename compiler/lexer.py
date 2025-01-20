from sly import Lexer

class my_lexer(Lexer):
    # Tokeny z gramatyki
    tokens = {
        PROCEDURE, PROGRAM, IS, BEGIN, END,                             # type: ignore
        IF, THEN, ELSE, ENDIF, WHILE, DO, ENDWHILE,                     # type: ignore
        REPEAT, UNTIL, FOR, FROM, TO, DOWNTO, ENDFOR,                   # type: ignore
        READ, WRITE,                                                    # type: ignore
        PIDENTIFIER, NUM, T,                                            # type: ignore
        ASSIGN, PLUS, MINUS, MULTIPLY, DIVIDE, MOD,                     # type: ignore
        EQUAL, NEQUAL, LESS, GREATER, LEQ, GEQ,                         # type: ignore
        LPAREN, RPAREN, LBRACKET, RBRACKET, SEMICOLON, COLON, COMMA     # type: ignore
    }

    # Ignorowane znaki (spacje, tabulatory)
    ignore = ' \t'

    # Definicje tokenów odpowiadające słowom kluczowym
    PROCEDURE = r'PROCEDURE'
    PROGRAM = r'PROGRAM'
    IS = r'IS'
    BEGIN = r'BEGIN'
    IF = r'IF'
    THEN = r'THEN'
    ELSE = r'ELSE'
    ENDWHILE = r'ENDWHILE'
    ENDIF = r'ENDIF'
    WHILE = r'WHILE'
    DO = r'DO'
    REPEAT = r'REPEAT'
    UNTIL = r'UNTIL'
    FOR = r'FOR'
    FROM = r'FROM'
    TO = r'TO'
    DOWNTO = r'DOWNTO'
    ENDFOR = r'ENDFOR'
    READ = r'READ'
    WRITE = r'WRITE'
    T = r'T'
    END = r'END'

    # Symboliczne tokeny
    ASSIGN = r':='
    PLUS = r'\+'
    MINUS = r'-'
    MULTIPLY = r'\*'
    DIVIDE = r'/'
    MOD = r'%'
    EQUAL = r'='
    NEQUAL = r'!='
    LESS = r'<'
    GREATER = r'>'
    LEQ = r'<='
    GEQ = r'>='
    LPAREN = r'\('
    RPAREN = r'\)'
    LBRACKET = r'\['
    RBRACKET = r'\]'
    SEMICOLON = r';'
    COLON = r':'
    COMMA = r','

    # Token identyfikatorów
    PIDENTIFIER = r'[_a-z]+'

    # Token liczb INT
    @_(r'[-]?\d+') # type: ignore
    def NUM(self, t):
        t.value = int(t.value)
        return t

    # Ignorowanie komentarzy
    @_(r'\#[^\n]*') # type: ignore
    def ignore_comment(self, t):
        self.lineno += t.value.count('\n')

    # Ignorowanie nowej linii
    @_(r'\n+') # type: ignore
    def ignore_newline(self, t):
        self.lineno += len(t.value)

    # Obsługa błędów
    def error(self, t):
        print(f"ERROR LEXER: illegal character {t.value[0]} on line {self.lineno}")
        self.index += 1
        #exit(1)

if __name__ == '__main__':
    data0 = 'x = 3 + 42 * (s - t)'
    data1 = '''
    PROGRAM IS #hehe
    BEGIN
    .?
        x := 10;
        IF x < 20 THEN
            WRITE x;
        ENDIF;
    END;
    '''

    lexer = my_lexer()
    for token in lexer.tokenize(data1):
        print(token)
