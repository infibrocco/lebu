from .Lexer import Lexer
from .Parser import Parser
from .Compiler import Compiler
from .AST import Program
import json
import time
from argparse import ArgumentParser, Namespace, ArgumentError

from llvmlite import ir
import llvmlite.binding as llvm
from ctypes import CFUNCTYPE, c_int, c_float  # noqa: F401
import os
# pyinstaller --onefile --name lebu --icon=assets/lebu_icon.ico main.py

LEXER_DEBUG: bool = True
PARSER_DEBUG: bool = True
COMPILER_DEBUG: bool = True
RUN_CODE: bool = False

PROD_DEBUG: bool = True


def parse_arguments() -> Namespace:
    arg_parser: ArgumentParser = ArgumentParser(description="LebuLang v0.0.4-alpha")
    # Required Arguments
    arg_parser.add_argument(
        "file_path",
        type=str,
        help="Path to your entry point lebu file (ex. `main.lebu`)",
    )
    arg_parser.add_argument(
        "--debug", action="store_true", help="Prints internal debug information"
    )

    return arg_parser.parse_args()


def main(args: Namespace) -> None:
    global RUN_CODE, PROD_DEBUG, COMPILER_DEBUG, LEXER_DEBUG, PARSER_DEBUG
    if not args.file_path:
        raise ArgumentError("Must provide input file path.")

    if args.debug:
        PROD_DEBUG = True

    # Read from input file
    # with open(os.path.join(os.path.abspath(os.curdir), args.file_path), "r") as f:
    with open(args.file_path, "r") as f:
        code: str = f.read()

    if LEXER_DEBUG:
        print("===== LEXER DEBUG =====")
        debug_lex: Lexer = Lexer(source=code)
        while debug_lex.current_char is not None:
            print(debug_lex.next_token())

    lexer: Lexer = Lexer(source=code)
    parser: Parser = Parser(lexer=lexer)

    parse_st: float = time.perf_counter_ns()
    program: Program = parser.parse_program()
    parse_et: float = time.perf_counter_ns()
    if len(parser.errors) > 0:
        for err in parser.errors:
            print(err)
        exit(1)

    if PARSER_DEBUG:
        print("===== PARSER DEBUG =====")
        with open(os.path.join(os.path.abspath(os.curdir), "debug/ast.json"), "w") as f:
            json.dump(program.json(), f, indent=4)
        print("Wrote AST to debug/ast.json successfully")

    c: Compiler = Compiler()
    compiler_st: float = time.perf_counter_ns()
    c.compile(node=program)
    compiler_et: float = time.perf_counter_ns()

    # Output steps
    module: ir.Module = c.module
    module.triple = llvm.get_default_triple()

    if COMPILER_DEBUG:
        print("==== COMPILER DEBUG ====")
        with open(os.path.join(os.path.abspath(os.curdir), "debug/ir.ll"), "w") as f:
            f.write(str(module))
        print("Wrote IR to debug/ir.ll successfully")

    if len(c.errors) > 0:
        print("==== COMPILER ERRORS ====")
        for err in c.errors:
            print(err)
        exit(1)

    if RUN_CODE:
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

        try:
            llvm_ir_parsed = llvm.parse_assembly(str(module))
            llvm_ir_parsed.verify()
        except Exception as e:
            print(e)
            raise

        target_machine = llvm.Target.from_default_triple().create_target_machine()

        engine = llvm.create_mcjit_compiler(llvm_ir_parsed, target_machine)
        engine.finalize_object()

        # Run the function with the name 'main'. This is the entry point function of the entire program
        entry = engine.get_function_address("main")
        cfunc = CFUNCTYPE(c_int)(entry)

        st = time.perf_counter_ns()

        result = cfunc()

        et = time.perf_counter_ns()

        if PROD_DEBUG:
            print(
                f"\n\n=== Parsed in: {parse_et - parse_st} ns. {(parse_et - parse_st)/1_000_000} ms. ==="
            )
            print(
                f"=== Compiled in: {compiler_et - compiler_st} ns. {(compiler_et - compiler_st)/1_000_000} ms. ==="
            )
        print(
            f"=== Executed in {et - st} ns. {(et - st)/1_000_000} ms. ===\n\nProgram returned: {result}"
        )


if __name__ == "__main__":
    args = parse_arguments()
    try:
        main(args)
    except Exception as e:
        print(e)
        print(args)
        print(os.path.abspath(os.curdir))
