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
    def test_string_literal(self):
        inp = 'let x = "Hello, World!" in x;'
        ast, errors, context, scope = run_code(inp)
        self.assertEqual(0, len(errors), f"Expects 0 errors, but got {len(errors)}")

    def test_number_literal(self):
        inp = 'let x = 42 in x;'
        ast, errors, context, scope = run_code(inp)
        self.assertEqual(0, len(errors), f"Expects 0 errors, but got {len(errors)}")

    def test_boolean_literal(self):
        inp = 'let x = true, y = false in x;'
        ast, errors, context, scope = run_code(inp)
        self.assertEqual(0, len(errors), f"Expects 0 errors, but got {len(errors)}")

    def test_redef_var(self):
        inp = 'let x = 4, x = x + 5 in x;'
        ast, errors, context, scope = run_code(inp)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")

    def test_simple_type_instance(self):
        inp = '''
        type A { }
        
        let x = new A() in x;
        '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")

    def test_invalid_arithmetic(self):
        inp = 'let x = 42 + "Hello, World!" in x;'
        ast, errors, context, scope = run_code(inp)
        self.assertEqual(1, len(errors), f"Expects 1 error, but got {len(errors)}")

    def test_invalid_boolean_operation(self):
        inp = 'let x = 4 | false in x;'
        ast, errors, context, scope = run_code(inp)
        self.assertEqual(1, len(errors), f"Expects 1 error, but got {len(errors)}")

    def test_invalid_assigment_operation(self):
        inp = 'let x = 4 in x := false;'
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors), f"Expects 1 error, but got {len(errors)}")
