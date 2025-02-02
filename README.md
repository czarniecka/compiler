# Imperative Language Compiler

## Author

Aleksandra Czarniecka 272385

## Project Description

This project was developed as part of the Formal Languages and Translation Techniques course at Wrocław University of Science and Technology during the winter semester of 2024/2025.

This is a compiler for a simple imperative language that translates source code into virtual machine code. The compiler supports variables, arrays, procedures, basic arithmetic operations, and control structures such as loops and conditional statements.

## Project Structure

The project consists of the following files in folder `compiler`:

- `lexer.py` – a lexical analyzer that tokenizes the source code.
- `parser.py` – a syntax analyzer that constructs a simple syntax tree represented by nested tuples from the tokens.
- `symbol_table.py` – manages the symbol table, storing information about variables, iterators, arrays, and procedures.
- `code_generator.py` – a module that generates virtual machine code based on the tree constructed by the parser.
- `compiler.py` – the main script that runs the entire compilation process.

## Additional Directories and Files

The following directories and files were provided by the course instructor (Maciej Gębala):

- `tests` directory – example programs for verifying the correctness of the generated code.
- `programs` directory – additional auxiliary scripts.
- `virtual_machine` directory – virtual machine code.
- `gramatyka.txt` – imperative language grammar.
- `labor4.pdf` – project specification.

## Installation and Execution

### Requirements

- Python 3.10 (`sudo apt install python3.10`)
- `sly` library for syntax analysis (`pip install sly`)

### Compilation

To compile the program, run the compiler from the terminal:

```sh
python3 compiler.py <input_file> <output_file>
```

where:
- `<input_file>` – the name of the file containing the source code in the imperative language,
- `<output_file>` – the name of the file where the generated virtual machine code will be saved.

## Notes

In the `example6.imp` file, the variable 'j' should be removed from the program declaration due to overloading (it is used as an iterator in the program).
In the `example8.imp` file, on line 25, the array name 'tab' should be replaced with the correct name 't'.
