import unittest

from src.evaluation import evaluate_reverse_parse
from src.lexer.hulk_lexer import HulkLexer
from src.parser.hulk_parser import HulkParser
from src.semantics.semantic_analysis_pipeline import semantic_analysis_pipeline

lexer = HulkLexer()
parser = HulkParser()


def run_code(inp: str, debug=False):
    tokens, errors = lexer(inp)
    assert not errors
    derivation, operations, errors = parser(tokens)
    assert not errors
    ast = evaluate_reverse_parse(derivation, operations, tokens)
    ast, errors, context, scope = semantic_analysis_pipeline(ast, debug)
    return ast, errors, context, scope


class TestHulkLoops(unittest.TestCase):

    def test_circular_inheritance(self):
        inp = ('''
                type A inherits B {
                    x = x + 5;
                }
                type B(x) inherits A(x^2) {
                    x = x + 5;
                }
                let x = 9 in new A(x);
                ''')
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors), f"Expects 1 error, but got {len(errors)}")

    def test_inherits_params(self):
        inp = ('''
                type A inherits B {
                    x = x + 5;
                }
                type B(x) {
                    x = x + 5;
                }
                let x = 9 in new A(x);
                ''')
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")

    def test_hierarchy(self):
        inp = ('''
        type A(x) {
            x = x + 5;
        }
        type B(x) inherits A(x^2) {
            x = x + 5;
        }
        let x = 9 in new B(x);
        ''')
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")

    def test_pol_hierarchy(self):
        inp = ('''
        type A(x) {
            x = x + 5;
            sum(y) => self.x + y; 
        }
        type B(x) inherits A(x^2) {
            x = x + 5;
            sum(y) => self.x + y; 
        }
        let x = 9 in new B(x);
        ''')
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")

    def test_pol_hierarchy_2(self):
        inp = ('''
        type A(x) {
            x = x + 5;
            sum(y) => self.x + y; 
        }
        type B(x) inherits A(x^2) {
            x = x + 5;
            sum(y: Object) => 5; 
        }
        let x = 9 in new B(x);
        ''')
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors), f"Expects 1 error, but got {len(errors)}")

    def test_for_loop(self):
        inp = 'for (x in range(0, 10)) print(x);'
        ast, errors, context, scope = run_code(inp)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")

    def test_for_translation(self):
        inp = '''
        let iterable = range(0, 10) in
            while (iterable.next())
            let x = iterable.current() in print(x);'''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")

    def test_call_to_not_defined_function(self):
        inp = '''
        let iterable = t().next() in
            let x = iterable.current() in print(x);'''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors), f"Expects 1 error, but got {len(errors)}")

    def test_not_defined_ver(self):
        inp = '''
        let iterable = t.next() in
            let x = iterable.current() in print(x);'''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors), f"Expects 1 error, but got {len(errors)}")

    def test(self):
        type_test = """
        type A(q : Number, r : Number) {
        f : Number = q;
        p : Number = r;

        getsum(s: Number) : Number => self.f + self.p + s;
        }

        function operate(x : Number, y : Object) : String {
            print((x + (y as Number)) as Object);
        }

        let a : Number = 6 in
        let b : Number = a * 7, c : Object = b in
        print(operate(a, b));
        """

        assert run_code(type_test, True)
