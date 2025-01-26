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
    ENDWHILE  = r'ENDWHILE'
    PROGRAM   = r'PROGRAM'
    DOWNTO    = r'DOWNTO'
    ENDFOR    = r'ENDFOR'
    REPEAT    = r'REPEAT'
    BEGIN     = r'BEGIN'
    ENDIF     = r'ENDIF'
    UNTIL     = r'UNTIL'
    WHILE     = r'WHILE'
    WRITE     = r'WRITE'
    ELSE      = r'ELSE'
    FROM      = r'FROM'
    READ      = r'READ'
    THEN      = r'THEN'
    END       = r'END'
    FOR       = r'FOR'
    DO        = r'DO'
    IF        = r'IF'
    IS        = r'IS'
    TO        = r'TO'
   
    
    # Symboliczne tokeny
    ASSIGN      = r':='
    NEQUAL      = r'!='
    GEQ         = r'>='
    LEQ         = r'<='
    EQUAL       = r'='
    GREATER     = r'>'
    LESS        = r'<'
    COMMA       = r','
    SEMICOLON   = r';'
    COLON       = r':'
    PLUS        = r'\+'
    MINUS       = r'\-'
    MULTIPLY    = r'\*'
    DIVIDE      = r'\/'
    MOD         = r'\%'
    LBRACKET    = r'\['
    RBRACKET    = r'\]'
    LPAREN      = r'\('
    RPAREN      = r'\)'

    
    NUM = r'\d+'
    T = r'T'
    # Token identyfikatorów
    PIDENTIFIER = r'[_a-z]+'

    @_(r'\d+')
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
