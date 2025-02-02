from lexer import my_lexer
from parser import my_parser
from symbol_table import SymbolTable, Variable, Iterator, Array
from code_generator import CodeGenerator

if __name__ == "__main__":
    lexer = my_lexer()
    parser = my_parser()
    file_path = "../tests/error8.imp"
    
    try:
        # Otwieramy plik źródłowy
        with open(file_path, "r") as file:
            source_code = file.read()
        
        # Tokenizowanie programu źródłowego
        tokens = lexer.tokenize(source_code)
        
        # Parsowanie i generowanie kodu
        asm_code = parser.parse(tokens)
        
        print("\nGenerated Assembler Code:")
        print(asm_code)
        
        # Zapisanie wygenerowanego kodu do pliku
        with open("output.mr", "w") as f:
            f.write(asm_code)
        
        print("\nAssembler code saved to 'output.mr'.")

    except Exception as e:
        print(f"Error: {e}")
