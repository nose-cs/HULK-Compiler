import sys

from hulk_grammar.hulk_grammar import G
from lexer.hulk_lexer import HulkLexer
from parsing import LR1Parser


def run_pipeline(input_path, output_path):
    with open(input_path) as f:
        text = f.read()

    hulk_lexer = HulkLexer()
    tokens, errors = hulk_lexer(text)

    if errors:
        for err in errors:
            print(err)
        raise Exception()

    hulk_parser = LR1Parser(G)
    ast = hulk_parser(tokens)

    if ast.errors:
        for err in ast.errors:
            print(err)
        raise Exception()

    return ast


if __name__ == "__main__":
    input_ = sys.argv[1]
    output_ = sys.argv[2]
    run_pipeline(input_, output_)
