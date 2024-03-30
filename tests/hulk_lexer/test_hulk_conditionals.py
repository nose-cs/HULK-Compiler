import unittest

import src.hulk_grammar.hulk_grammar as hulk_grammar
from src.lexer.hulk_lexer import HulkLexer

lexer = HulkLexer()


class TestHulkConditionals(unittest.TestCase):
    def test_with_two_string(self):
        inp = 'let a = 42 in if (a % 2 == 0) print("Even") else print("odd");'
        expected = [hulk_grammar.let, hulk_grammar.idx, hulk_grammar.equal, hulk_grammar.number_literal, hulk_grammar.in_,
                    hulk_grammar.if_, hulk_grammar.opar, hulk_grammar.idx, hulk_grammar.mod, hulk_grammar.number_literal,
                    hulk_grammar.eq, hulk_grammar.number_literal, hulk_grammar.cpar, hulk_grammar.idx, hulk_grammar.opar,
                    hulk_grammar.string_literal, hulk_grammar.cpar, hulk_grammar.else_, hulk_grammar.idx, hulk_grammar.opar,
                    hulk_grammar.string_literal, hulk_grammar.cpar, hulk_grammar.semicolon, hulk_grammar.G.EOF]
        tokens, errors = lexer(inp)
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_expression_block(self):
        inp = 'let a = 42 in\nif (a % 2 == 0) {\nprint(a);\nprint("Even");}\nelse print("Odd");'
        expected = [hulk_grammar.let, hulk_grammar.idx, hulk_grammar.equal, hulk_grammar.number_literal, hulk_grammar.in_,
                    hulk_grammar.if_, hulk_grammar.opar, hulk_grammar.idx, hulk_grammar.mod, hulk_grammar.number_literal,
                    hulk_grammar.eq, hulk_grammar.number_literal, hulk_grammar.cpar, hulk_grammar.obracket, hulk_grammar.idx,
                    hulk_grammar.opar, hulk_grammar.idx, hulk_grammar.cpar, hulk_grammar.semicolon, hulk_grammar.idx,
                    hulk_grammar.opar, hulk_grammar.string_literal, hulk_grammar.cpar, hulk_grammar.semicolon,
                    hulk_grammar.cbracket, hulk_grammar.else_, hulk_grammar.idx, hulk_grammar.opar,
                    hulk_grammar.string_literal, hulk_grammar.cpar, hulk_grammar.semicolon, hulk_grammar.G.EOF]
        tokens, errors = lexer(inp)
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_elif(self):
        inp = 'let a = 42, let mod = a % 3 in\nprint(\nif (mod == 0) "Magic"\nelif (mod % 3 == 1) "Woke"\nelse "Dumb"\n);'
        expected = [hulk_grammar.let, hulk_grammar.idx, hulk_grammar.equal, hulk_grammar.number_literal, hulk_grammar.comma,
                    hulk_grammar.let, hulk_grammar.idx, hulk_grammar.equal, hulk_grammar.idx, hulk_grammar.mod,
                    hulk_grammar.number_literal, hulk_grammar.in_, hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.if_,
                    hulk_grammar.opar, hulk_grammar.idx, hulk_grammar.eq, hulk_grammar.number_literal, hulk_grammar.cpar,
                    hulk_grammar.string_literal, hulk_grammar.elif_, hulk_grammar.opar, hulk_grammar.idx, hulk_grammar.mod,
                    hulk_grammar.number_literal, hulk_grammar.eq, hulk_grammar.number_literal, hulk_grammar.cpar, hulk_grammar.string_literal,
                    hulk_grammar.else_, hulk_grammar.string_literal, hulk_grammar.cpar, hulk_grammar.semicolon,
                    hulk_grammar.G.EOF]
        tokens, errors = lexer(inp)
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_nested_if(self):
        inp = 'let a = 42 in print(if (a % 2 == 0) "even" else "odd");'
        expected = [hulk_grammar.let, hulk_grammar.idx, hulk_grammar.equal, hulk_grammar.number_literal, hulk_grammar.in_,
                    hulk_grammar.idx, hulk_grammar.opar, hulk_grammar.if_, hulk_grammar.opar, hulk_grammar.idx,
                    hulk_grammar.mod, hulk_grammar.number_literal, hulk_grammar.eq, hulk_grammar.number_literal, hulk_grammar.cpar,
                    hulk_grammar.string_literal, hulk_grammar.else_, hulk_grammar.string_literal, hulk_grammar.cpar,
                    hulk_grammar.semicolon, hulk_grammar.G.EOF]
        tokens, errors = lexer(inp)
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")
