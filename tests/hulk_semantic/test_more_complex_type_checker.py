import unittest

from src.evaluation import evaluate_reverse_parse
from src.hulk_grammar.hulk_grammar import G
from src.lexer.hulk_lexer import HulkLexer
from src.parsing import LR1Parser
from src.semantics.semantic_analysis_pipeline import semantic_analysis_pipeline

lexer = HulkLexer()
parser = LR1Parser(G)


def run_code(inp: str, debug=False):
    tokens, errors = lexer(inp)
    assert not errors
    derivation, operations = parser([t.token_type for t in tokens])
    ast = evaluate_reverse_parse(derivation, operations, tokens)
    ast, errors, context, scope = semantic_analysis_pipeline(ast, debug)
    return ast, errors, context, scope


class TestHulkTypeInference(unittest.TestCase):
    def test_type_arguments_inference(self):
        inp = '''
        type A(x) {
        x = x + 5;
        }
        let x = 9 in new A(x);
        '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")