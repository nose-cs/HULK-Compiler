import unittest

import src.hulk_grammar.hulk_grammar as hulk_grammar
from src.lexer.hulk_lexer import HulkLexer

lexer = HulkLexer()


class TestHulkFunctions(unittest.TestCase):

    def test_function(self):
        expected = [hulk_grammar.function, hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.idx, hulk_grammar.cpar,
                    hulk_grammar.arrow, hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.idx, hulk_grammar.cpar,
                    hulk_grammar.div, hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.idx, hulk_grammar.cpar,
                    hulk_grammar.semicolon, hulk_grammar.G.EOF]
        tokens, errors = lexer('function tan(x) => sin(x) / cos(x);')
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_functions_and_expression(self):
        expected = [hulk_grammar.function, hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.idx, hulk_grammar.cpar,
                    hulk_grammar.arrow, hulk_grammar.number, hulk_grammar.div, hulk_grammar.idx, hulk_grammar.opar,
                    hulk_grammar.idx, hulk_grammar.cpar, hulk_grammar.semicolon, hulk_grammar.function,
                    hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.idx, hulk_grammar.cpar, hulk_grammar.arrow,
                    hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.idx, hulk_grammar.cpar, hulk_grammar.div,
                    hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.idx, hulk_grammar.cpar, hulk_grammar.semicolon,
                    hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.idx,
                    hulk_grammar.cpar, hulk_grammar.power2, hulk_grammar.number, hulk_grammar.plus, hulk_grammar.idx,
                    hulk_grammar.opar, hulk_grammar.idx, hulk_grammar.cpar, hulk_grammar.power2, hulk_grammar.number,
                    hulk_grammar.cpar, hulk_grammar.semicolon, hulk_grammar.G.EOF]

        tokens, errors = lexer(
            'function cot(x) => 1 / tan(x);\nfunction tan(x) => sin(x) / cos(x);\nprint(tan(PI) ** 2 + cot(PI) ** 2);')

        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_full_form_function(self):
        inp = 'function operate(x, y) {\nprint(x + y);\nprint(x - y);\nprint(x * y);\nprint(x / y);\n}'
        expected = [hulk_grammar.function, hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.idx, hulk_grammar.comma,
                    hulk_grammar.idx, hulk_grammar.cpar, hulk_grammar.obracket, hulk_grammar.idx, hulk_grammar.opar,
                    hulk_grammar.idx, hulk_grammar.plus, hulk_grammar.idx, hulk_grammar.cpar, hulk_grammar.semicolon,
                    hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.idx, hulk_grammar.minus, hulk_grammar.idx,
                    hulk_grammar.cpar, hulk_grammar.semicolon, hulk_grammar.idx, hulk_grammar.opar,
                    hulk_grammar.idx, hulk_grammar.star, hulk_grammar.idx, hulk_grammar.cpar, hulk_grammar.semicolon,
                    hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.idx, hulk_grammar.div, hulk_grammar.idx,
                    hulk_grammar.cpar, hulk_grammar.semicolon, hulk_grammar.cbracket, hulk_grammar.G.EOF]
        tokens, errors = lexer(inp)
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")


if __name__ == '__main__':
    unittest.main()
