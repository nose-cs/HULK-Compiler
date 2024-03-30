from pathlib import Path

from hulk_grammar.hulk_grammar import G
from lexer.hulk_lexer import HulkLexer
from parsing import LR1Parser
from src.code_gen.code_generator import CCodeGenerator
from src.errors import IOHulkError
from src.evaluation import evaluate_reverse_parse
from src.semantics.semantic_analysis_pipeline import semantic_analysis_pipeline


def run_pipeline(input_path: Path, output_path: Path, debug=False):
    if not input_path.match('*.hulk'):
        raise IOHulkError(IOHulkError.INVALID_EXTENSION, input_path)

    if debug:
        print("===================== READING FILE =====================")
    try:
        with open(input_path) as f:
            text = f.read()
    except FileNotFoundError:
        raise IOHulkError(IOHulkError.ERROR_READING_FILE, input_path)

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

    hulk_parser = LR1Parser(G)
    derivation, operations = hulk_parser([t.token_type for t in tokens])
    ast = evaluate_reverse_parse(derivation, operations, tokens)

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
        raise IOHulkError(IOHulkError.ERROR_WRITING_FILE, output_path)

    if debug:
        print("C code:")
        print(code)


if __name__ == "__main__":
    # input_ = sys.argv[1]
    # output_ = sys.argv[2]
    debug = True
    input_ = "./hello_world.hulk"
    output_ = "./hello_world.c"
    run_pipeline(Path(input_), Path(output_), debug)
