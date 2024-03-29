import unittest

import src.hulk_grammar.hulk_grammar as hulk_grammar
from src.lexer.hulk_lexer import HulkLexer

lexer = HulkLexer()


class TestHulkExpressions(unittest.TestCase):
    def test_number(self):
        expected = [hulk_grammar.number_literal, hulk_grammar.semicolon, hulk_grammar.G.EOF]
        tokens, errors = lexer('42;')
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_print(self):
        expected = [hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.number_literal, hulk_grammar.cpar, hulk_grammar.semicolon,
                    hulk_grammar.G.EOF]
        tokens, errors = lexer('print(42);')
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_string(self):
        expected = [hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.string_literal, hulk_grammar.cpar,
                    hulk_grammar.semicolon, hulk_grammar.G.EOF]
        tokens, errors = lexer('print("The message is \"Hello World\"");')
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_concat(self):
        expected = [hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.string_literal, hulk_grammar.amper,
                    hulk_grammar.number_literal, hulk_grammar.cpar, hulk_grammar.semicolon, hulk_grammar.G.EOF]
        tokens, errors = lexer('print("The meaning of life is " @ 42);')
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test5_built_in(self):
        expected = [hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.number_literal,
                    hulk_grammar.star, hulk_grammar.idx, hulk_grammar.cpar, hulk_grammar.power, hulk_grammar.number_literal,
                    hulk_grammar.plus, hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.number_literal, hulk_grammar.star,
                    hulk_grammar.idx, hulk_grammar.div, hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.number_literal,
                    hulk_grammar.comma, hulk_grammar.number_literal, hulk_grammar.cpar, hulk_grammar.cpar, hulk_grammar.cpar,
                    hulk_grammar.semicolon, hulk_grammar.G.EOF]
        tokens, errors = lexer('print(sin(2 * PI) ^ 2 + cos(3 * PI / log(4, 64)));')
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_expression_block(self):
        expected = [hulk_grammar.obracket, hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.number_literal, hulk_grammar.cpar,
                    hulk_grammar.semicolon, hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.idx, hulk_grammar.opar,
                    hulk_grammar.idx, hulk_grammar.div, hulk_grammar.number_literal, hulk_grammar.cpar, hulk_grammar.cpar,
                    hulk_grammar.semicolon, hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.string_literal,
                    hulk_grammar.cpar, hulk_grammar.semicolon, hulk_grammar.cbracket, hulk_grammar.G.EOF]
        tokens, errors = lexer('{\nprint(42);\n print(sin(PI/2));\n print("Hello World");\n}')
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")
