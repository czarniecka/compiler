from sly import Lexer

class MyLexer(Lexer):
    # Tokeny z gramatyki
    tokens = {
        PROCEDURE, PROGRAM, IS, BEGIN, END, 
        IF, THEN, ELSE, ENDIF, WHILE, DO, ENDWHILE,
        REPEAT, UNTIL, FOR, FROM, TO, DOWNTO, ENDFOR,
        READ, WRITE,
        IDENTIFIER, NUM, 
        ASSIGN, PLUS, MINUS, MULTIPLY, DIVIDE, MOD,
        EQUAL, NEQUAL, LESS, GREATER, LEQ, GEQ,
        LPAREN, RPAREN, LBRACKET, RBRACKET, SEMICOLON, COLON, COMMA
    }

    # Ignorowane znaki (spacje, tabulatory)
    ignore = ' \t'

    # Definicje tokenów odpowiadające słowom kluczowym
    PROCEDURE = r'PROCEDURE'
    PROGRAM = r'PROGRAM'
    IS = r'IS'
    BEGIN = r'BEGIN'
    END = r'END'
    IF = r'IF'
    THEN = r'THEN'
    ELSE = r'ELSE'
    ENDIF = r'ENDIF'
    WHILE = r'WHILE'
    DO = r'DO'
    ENDWHILE = r'ENDWHILE'
    REPEAT = r'REPEAT'
    UNTIL = r'UNTIL'
    FOR = r'FOR'
    FROM = r'FROM'
    TO = r'TO'
    DOWNTO = r'DOWNTO'
    ENDFOR = r'ENDFOR'
    READ = r'READ'
    WRITE = r'WRITE'

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

    # Tokeny identyfikatorów i liczb
    @_(r'[a-zA-Z_][a-zA-Z0-9_]*')
    def IDENTIFIER(self, t):
        return t

    @_(r'[-]?\d+')
    def NUM(self, t):
        t.value = int(t.value)
        return t

    # Ignorowanie komentarzy
    @_(r'\#[^\n]*')
    def ignore_comment(self, t):
        self.lineno += t.value.count('\n')

    # Ignorowanie nowej linii
    @_(r'\n+')
    def ignore_empty_line(self, t):
        self.lineno += len(t.value)

    # Obsługa błędów
    def error(self, t):
        Exception(f"ERROR LEXER: unvalid sign {t.value[0]} on line {self.lineno}")
        self.index += 1

if __name__ == '__main__':
    data = '''
    PROGRAM IS
    BEGIN
        x := 10;
        IF x < 20 THEN
            WRITE x;
        ENDIF;
    END;
    '''

    lexer = MyLexer()
    for token in lexer.tokenize(data):
        print(token)
