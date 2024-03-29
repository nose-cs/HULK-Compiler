import unittest

import src.hulk_grammar.hulk_grammar as hulk_grammar
from src.lexer.hulk_lexer import HulkLexer

lexer = HulkLexer()


class TestHulkLoops(unittest.TestCase):

    def test_while_loop_in_let_in(self):
        expected = [hulk_grammar.let, hulk_grammar.idx, hulk_grammar.equal, hulk_grammar.number_literal, hulk_grammar.in_,
                    hulk_grammar.while_, hulk_grammar.opar, hulk_grammar.idx, hulk_grammar.geq, hulk_grammar.number_literal,
                    hulk_grammar.cpar, hulk_grammar.obracket, hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.idx,
                    hulk_grammar.cpar, hulk_grammar.semicolon, hulk_grammar.idx, hulk_grammar.dest_eq, hulk_grammar.idx,
                    hulk_grammar.minus, hulk_grammar.number_literal, hulk_grammar.semicolon, hulk_grammar.cbracket,
                    hulk_grammar.G.EOF]
        tokens, errors = lexer('let a = 10 in while (a >= 0) {\nprint(a);\na := a - 1;\n}')
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_while_in_method(self):
        expected = [hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.idx, hulk_grammar.comma, hulk_grammar.idx,
                    hulk_grammar.cpar, hulk_grammar.arrow, hulk_grammar.while_, hulk_grammar.opar, hulk_grammar.idx,
                    hulk_grammar.gt, hulk_grammar.number_literal, hulk_grammar.cpar, hulk_grammar.let, hulk_grammar.idx,
                    hulk_grammar.equal, hulk_grammar.idx, hulk_grammar.mod, hulk_grammar.idx, hulk_grammar.in_,
                    hulk_grammar.obracket, hulk_grammar.idx, hulk_grammar.dest_eq, hulk_grammar.idx,
                    hulk_grammar.semicolon, hulk_grammar.idx, hulk_grammar.dest_eq, hulk_grammar.idx,
                    hulk_grammar.semicolon, hulk_grammar.cbracket, hulk_grammar.semicolon, hulk_grammar.G.EOF]
        tokens, errors = lexer('gcd(a, b) => while (a > 0)\nlet m = a % b in {\nb := a;\na := m;\n};')
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_for_loop(self):
        inp = 'for (x in range(0, 10)) print(x);'
        expected = [hulk_grammar.for_, hulk_grammar.opar, hulk_grammar.idx, hulk_grammar.in_,
                    hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.number_literal, hulk_grammar.comma, hulk_grammar.number_literal,
                    hulk_grammar.cpar, hulk_grammar.cpar, hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.idx,
                    hulk_grammar.cpar, hulk_grammar.semicolon, hulk_grammar.G.EOF]
        tokens, errors = lexer(inp)
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_for_translation(self):
        inp = 'let iterable = range(0, 10) in\nwhile (iterable.next())\nlet x = iterable.current() in\nprint(x);'
        expected = [hulk_grammar.let, hulk_grammar.idx, hulk_grammar.equal, hulk_grammar.idx, hulk_grammar.opar,
                    hulk_grammar.number_literal, hulk_grammar.comma, hulk_grammar.number_literal, hulk_grammar.cpar, hulk_grammar.in_,
                    hulk_grammar.while_, hulk_grammar.opar, hulk_grammar.idx, hulk_grammar.dot, hulk_grammar.idx,
                    hulk_grammar.opar, hulk_grammar.cpar, hulk_grammar.cpar, hulk_grammar.let, hulk_grammar.idx,
                    hulk_grammar.equal, hulk_grammar.idx, hulk_grammar.dot, hulk_grammar.idx, hulk_grammar.opar,
                    hulk_grammar.cpar, hulk_grammar.in_, hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.idx,
                    hulk_grammar.cpar, hulk_grammar.semicolon, hulk_grammar.G.EOF]
        tokens, errors = lexer(inp)
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

