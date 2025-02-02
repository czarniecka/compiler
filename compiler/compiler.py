import sys
from lexer import my_lexer
from parser import my_parser

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 compiler.py <in_file> <out_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    lexer = my_lexer()
    parser = my_parser()
    
    try:
        with open(input_file, "r") as file:
            source_code = file.read()
        
        tokens = lexer.tokenize(source_code)
        asm_code = parser.parse(tokens)

        with open(output_file, "w") as f:
            f.write(asm_code)
        
        print(f"\nAssembler code saved to '{output_file}'.")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
