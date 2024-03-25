import unittest

import src.hulk_grammar.hulk_grammar as hulk_grammar
from src.lexer.hulk_lexer import HulkLexer

lexer = HulkLexer()


class TestHulkNumbers(unittest.TestCase):
    def test_simple_number(self):
        inp = '42'
        expected = [hulk_grammar.number, hulk_grammar.G.EOF]
        tokens, errors = lexer(inp)
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_simple_float_number(self):
        inp = '42.0'
        expected = [hulk_grammar.number, hulk_grammar.G.EOF]
        tokens, errors = lexer(inp)
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_negative_number(self):
        inp = '-42'
        expected = [hulk_grammar.minus, hulk_grammar.number, hulk_grammar.G.EOF]
        tokens, errors = lexer(inp)
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_negative_float_number(self):
        inp = '-42.0'
        expected = [hulk_grammar.minus, hulk_grammar.number, hulk_grammar.G.EOF]
        tokens, errors = lexer(inp)
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_number_with_double_dot(self):
        inp = '42.0.0'
        expected = [hulk_grammar.number, hulk_grammar.dot, hulk_grammar.number, hulk_grammar.G.EOF]
        tokens, errors = lexer(inp)
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_number_with_double_dot_and_negative(self):
        inp = '-42.0.0'
        expected = [hulk_grammar.minus, hulk_grammar.number, hulk_grammar.dot, hulk_grammar.number, hulk_grammar.G.EOF]
        tokens, errors = lexer(inp)
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_number_end_with_dot(self):
        inp = '42.'
        expected = [hulk_grammar.number, hulk_grammar.dot, hulk_grammar.G.EOF]
        tokens, errors = lexer(inp)
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_negative_number_end_with_dot(self):
        inp = '-42.'
        expected = [hulk_grammar.minus, hulk_grammar.number, hulk_grammar.dot, hulk_grammar.G.EOF]
        tokens, errors = lexer(inp)
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_numbers_starting_with_zero(self):
        expected = [hulk_grammar.G.EOF]
        tokens, errors = lexer('037.90')
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(1, len(errors), f"Expects 1 errors, but got {len(errors)}")


if __name__ == '__main__':
    unittest.main()
