import subprocess
import sys
from pathlib import Path

from lexer.hulk_lexer import HulkLexer
from src.code_gen.code_generator import CCodeGenerator
from src.errors import IOHulkError
from src.evaluation import evaluate_reverse_parse
from src.parser.hulk_parser import HulkParser
from src.semantics.semantic_analysis_pipeline import semantic_analysis_pipeline


def run_pipeline(input_path: Path):
    if not input_path.match('*.hulk'):
        raise IOHulkError(IOHulkError.INVALID_EXTENSION, input_path)

    try:
        with open(input_path) as f:
            text = f.read()
    except FileNotFoundError:
        raise IOHulkError(IOHulkError.ERROR_READING_FILE, input_path)

    hulk_lexer = HulkLexer()
    tokens, lexicographic_errors = hulk_lexer(text)

    if lexicographic_errors:
        for err in lexicographic_errors:
            print(err)
        return

    hulk_parser = HulkParser()
    derivation, operations, syntactic_errors = hulk_parser(tokens)
    ast = evaluate_reverse_parse(derivation, operations, tokens)

    if syntactic_errors:
        for err in syntactic_errors:
            print(err)
        return

    ast, semantic_errors, context, scope = semantic_analysis_pipeline(ast)

    if semantic_errors:
        for err in semantic_errors:
            print(err)
        return

    code_generator = CCodeGenerator()
    code = code_generator(ast, context)

    try:
        with open('output.c', 'w') as f:
            f.write(code)
    except FileNotFoundError:
        raise IOHulkError(IOHulkError.ERROR_WRITING_FILE, 'output.c')

    subprocess.run(["gcc", "output.c", "-o", "output.exe"], shell=True)
    subprocess.run(['start', 'cmd', '/k', 'output.exe'], shell=True)


if __name__ == "__main__":
    input_ = sys.argv[1]
    output_ = sys.argv[2]
    run_pipeline(Path(input_))
