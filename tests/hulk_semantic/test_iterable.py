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


class TestHulkLoops(unittest.TestCase):

    def test_doesnt_conform_to_protocol(self):
        inp = ('''
        function f(x: Range): Iterable => x;
        let x = range(10, 20) as Iterable in f(x);
        ''')
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors), f"Expects 1 error, but got {len(errors)}")

    def test_conforms_to_protocol(self):
        inp = ('''
        function f(x: Iterable) => x;
        let x = range(10, 20) in f(x);
        ''')
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")

    def test_is_iterable(self):
        inp = ('''
        type MyRange(min:Number, max:Number) {
            min = min;
            max = max;
            current = min - 1;
        
            next(): Bool => (self.current := self.current + 1) < self.max;
            current(): Number => self.current;
        }
        let x = new MyRange(1, 100) in x is Iterable;
        ''')
        ast, errors, context, scope = run_code(inp)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")

    def test_invalid_cast_to_iterable(self):
        inp = ('''
        type MyRange(min:Number, max:Number) {
            min = min;
            max = max;
            current = min - 1;

            next(): Bool => (self.current := self.current + 1) < self.max;
            current(): Number => self.current;
        }

        type X {
            current() => true;
            next() => true;
        }

        let x = new MyRange(1, 100), y: Iterable = new X() in x as Iterable;
        ''')
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")

    def test____(self):
        inp = ('''
            type X {
                current() => true;
                next() => 5;
            }

            let y: Iterable = new X() in y;
            ''')
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors), f"Expects 1 error, but got {len(errors)}")

    def test_conf(self):
        inp = ('''
            type X {
                current() => true;
                next() => true;
            }

            let y: Iterable = new X() in y;
            ''')
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")
