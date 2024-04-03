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


class TestHulkVectors(unittest.TestCase):

    def test_while_loop_in_let_in(self):
        inp = ('''
        for (x in [5, 6,7])
            print(x);
            ''')
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")

    def test_while_in_method(self):
        inp = '''
        for (x in ["hola", 9])
            print(x);
        '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")

    def test_while_in_method_(self):
        inp = '''
           for (x in [9 + "hola"]) print(x);
           '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors), f"Expects 1 error, but got {len(errors)}")

    def test__(self):
        inp = '''
           for (x in [9 + 3, 50]) x[4] := 8;
           '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors), f"Expects 1 error, but got {len(errors)}")

    def test___(self):
        inp = '''
           let x = [1,2,3] in x[7] := 4;
           '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")

    def test_force_object_return(self):
        inp = '''
           let x: Iterable = [1,2,3] in x[7] + 10;
           '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors), f"Expects 1 error, but got {len(errors)}")

    def test_force_(self):
        inp = '''
           let x = 5 + "20" in x[7] + 10;
           '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors), f"Expects 1 error, but got {len(errors)}")

    def test_invalid_assigment(self):
        inp = '''
           let x = [7,8,9] in x := [new Object()];
           '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors), f"Expects 1 error, but got {len(errors)}")

    def test_valid_assigment(self):
        inp = '''
              let x = ["casa", 7, 8] in x := ["hola"];
              '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")
