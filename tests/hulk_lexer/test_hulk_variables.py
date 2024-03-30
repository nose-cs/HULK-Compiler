import unittest

import src.hulk_grammar.hulk_grammar as hulk_grammar
from src.lexer.hulk_lexer import HulkLexer

lexer = HulkLexer()


# todo add all variables examples just in case

class TestHulkVariables(unittest.TestCase):
    def test_let_in(self):
        inp = 'let msg = "Hello World" in print(msg);'
        expected = [hulk_grammar.let, hulk_grammar.idx, hulk_grammar.equal, hulk_grammar.string_literal, hulk_grammar.in_,
                    hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.idx, hulk_grammar.cpar, hulk_grammar.semicolon,
                    hulk_grammar.G.EOF]
        tokens, errors = lexer(inp)
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    # -------------------------------------semantic equivalent---------------------------------------------------------
    def test_let_in_with_2_vars(self):
        inp = 'let number = 42, text = "The meaning of life is" in print(text @ number);'
        expected = [hulk_grammar.let, hulk_grammar.idx, hulk_grammar.equal, hulk_grammar.number_literal, hulk_grammar.comma,
                    hulk_grammar.idx, hulk_grammar.equal, hulk_grammar.string_literal, hulk_grammar.in_, hulk_grammar.idx,
                    hulk_grammar.opar, hulk_grammar.idx, hulk_grammar.amper, hulk_grammar.idx, hulk_grammar.cpar,
                    hulk_grammar.semicolon, hulk_grammar.G.EOF]
        tokens, errors = lexer(inp)
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_let_in_with_2_vars_but_nested(self):
        inp = 'let number = 42 in let text = "The meaning of life is" in print(text @ number);'
        expected = [hulk_grammar.let, hulk_grammar.idx, hulk_grammar.equal, hulk_grammar.number_literal, hulk_grammar.in_,
                    hulk_grammar.let, hulk_grammar.idx, hulk_grammar.equal, hulk_grammar.string_literal, hulk_grammar.in_,
                    hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.idx, hulk_grammar.amper, hulk_grammar.idx,
                    hulk_grammar.cpar, hulk_grammar.semicolon, hulk_grammar.G.EOF]
        tokens, errors = lexer(inp)
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_let_in_with_2_vars_but_associative(self):
        inp = 'let number = 42 in (let text = "The meaning of life is" in (print(text @ number)));'
        expected = [hulk_grammar.let, hulk_grammar.idx, hulk_grammar.equal, hulk_grammar.number_literal, hulk_grammar.in_,
                    hulk_grammar.opar, hulk_grammar.let, hulk_grammar.idx, hulk_grammar.equal,
                    hulk_grammar.string_literal,
                    hulk_grammar.in_, hulk_grammar.opar, hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.idx,
                    hulk_grammar.amper, hulk_grammar.idx, hulk_grammar.cpar, hulk_grammar.cpar,
                    hulk_grammar.cpar,
                    hulk_grammar.semicolon, hulk_grammar.G.EOF]
        tokens, errors = lexer(inp)
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    # ----------------------------------------------------------------------------------------------------------------#

    def test_let_in_block(self):
        inp = 'let a = 5, b = 10, c = 20 in {\nprint(a+b);\nprint(b*c);\nprint(c/a);\n}'
        expected = [hulk_grammar.let, hulk_grammar.idx, hulk_grammar.equal, hulk_grammar.number_literal, hulk_grammar.comma,
                    hulk_grammar.idx, hulk_grammar.equal, hulk_grammar.number_literal, hulk_grammar.comma, hulk_grammar.idx,
                    hulk_grammar.equal, hulk_grammar.number_literal, hulk_grammar.in_, hulk_grammar.obracket, hulk_grammar.idx,
                    hulk_grammar.opar, hulk_grammar.idx, hulk_grammar.plus, hulk_grammar.idx, hulk_grammar.cpar,
                    hulk_grammar.semicolon, hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.idx, hulk_grammar.star,
                    hulk_grammar.idx, hulk_grammar.cpar, hulk_grammar.semicolon, hulk_grammar.idx, hulk_grammar.opar,
                    hulk_grammar.idx, hulk_grammar.div, hulk_grammar.idx, hulk_grammar.cpar, hulk_grammar.semicolon,
                    hulk_grammar.cbracket, hulk_grammar.G.EOF]
        tokens, errors = lexer(inp)
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")


if __name__ == '__main__':
    unittest.main()
