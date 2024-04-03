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


class TestHulkBase(unittest.TestCase):

    def test_cannot_use_base_outside_of_a_method(self):
        inp = ('''
        let a = base(a, b, c) in a;
        ''')
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors), f"Expects 1 error, but got {len(errors)}")

    # todo
    def test_cannot_declare_a_function(self):
        inp = ('''
        function base(a) => a + 8;
        let a = base(6, 7, 8) in a;
        ''')
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors), f"Expects 1 error, but got {len(errors)}")

    def test_valid_base_call(self):
        inp = '''
            type B {
                f(a, b) => a + b;
           }
           
           type A inherits B {
                f(a, b) => base(a, b) + base(a,b);
           }
           
           let x = 5 in x;
        '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")

    def test_base_call_with_bad_args(self):
        inp = '''
            type B {
                f(a, b) => a + b;
           }

           type A inherits B {
                f(a, b) => base(a) + base(a,b);
           }

           let x = 5 in x;
        '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors), f"Expects 1 error, but got {len(errors)}")
