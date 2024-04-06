import sys
from pathlib import Path

from src.code_gen.code_generator import CCodeGenerator
from src.errors import HulkIOError
from src.evaluation import evaluate_reverse_parse
from src.lexer.hulk_lexer import HulkLexer
from src.parser.hulk_parser import HulkParser
from src.semantics.semantic_analysis_pipeline import semantic_analysis_pipeline


def run_pipeline(input_path: Path, output_path: Path, debug=False):
    if not input_path.match('*.hulk'):
        raise HulkIOError(HulkIOError.INVALID_EXTENSION % input_path)

    if debug:
        print("===================== READING FILE =====================")
    try:
        with open(input_path) as f:
            text = f.read()
    except FileNotFoundError:
        raise HulkIOError(HulkIOError.ERROR_READING_FILE % input_path)

    if debug:
        print("Hulk code:")
        print(text)

    if debug:
        print("===================== LEXICAL ANALYSIS =====================")
    hulk_lexer = HulkLexer()
    tokens, lexicographic_errors = hulk_lexer(text)

    if debug:
        print("Tokens:")
        for token in tokens:
            print(token)

    if lexicographic_errors:
        for err in lexicographic_errors:
            print(err)
        return

    if debug:
        print("===================== SYNTACTIC ANALYSIS =====================")

    hulk_parser = HulkParser()
    derivation, operations, syntactic_errors = hulk_parser(tokens)
    ast = evaluate_reverse_parse(derivation, operations, tokens)

    if syntactic_errors:
        for err in syntactic_errors:
            print(err)
        return

    if debug:
        print("===================== SEMANTIC ANALYSIS =====================")
    ast, semantic_errors, context, scope = semantic_analysis_pipeline(ast, debug)

    if semantic_errors:
        for err in semantic_errors:
            print(err)
        return

    if debug:
        print("===================== CODE GENERATION =====================")

    code_generator = CCodeGenerator()
    code = code_generator.generate(ast, context)

    try:
        with open(output_path, 'w') as f:
            f.write(code)
    except FileNotFoundError:
        raise HulkIOError(HulkIOError.ERROR_WRITING_FILE % output_path)

    if debug:
        print("C code:")
        print(code)


if __name__ == "__main__":
    input_ = sys.argv[1]
    output_ = sys.argv[2]
    debug = False
    run_pipeline(Path(input_), Path(output_), debug)
