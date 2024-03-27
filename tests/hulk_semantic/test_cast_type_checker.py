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


class TestHulkCastTypeInference(unittest.TestCase):
    def test_num_object_dynamic_type_checking(self):
        inp = 'let a = 4 + 5 is Object in a;'
        ast, errors, context, scope = run_code(inp)
        self.assertEqual(0, len(errors), f"Expects 0 errors, but got {len(errors)}")

    def test_num_str_dynamic_type_checking(self):
        inp = 'let a = 92 is String in a;'
        ast, errors, context, scope = run_code(inp)
        self.assertEqual(0, len(errors), f"Expects 0 errors, but got {len(errors)}")

    def test_object_num_dynamic_type_checking(self):
        inp = 'let a = new Object(), b = a is Number in b;'
        ast, errors, context, scope = run_code(inp)
        self.assertEqual(0, len(errors), f"Expects 0 errors, but got {len(errors)}")

    def test_string_bool_downcast(self):
        inp = '''
        type A {}
        let a = "Hola" as A in a;
        '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors), f"Expects 1 error, but got {len(errors)}")
