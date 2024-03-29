import unittest

import src.hulk_grammar.hulk_grammar as hulk_grammar
from src.lexer.hulk_lexer import HulkLexer

lexer = HulkLexer()


class TestHulkStrings(unittest.TestCase):
    def test_simple_string(self):
        inp = '"Hello, World!"'
        expected = [hulk_grammar.string_literal, hulk_grammar.G.EOF]
        tokens, errors = lexer(inp)
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_string_with_escape(self):
        inp = '"Hello, \"World!\""'
        expected = [hulk_grammar.string_literal, hulk_grammar.G.EOF]
        tokens, errors = lexer(inp)
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_unfinished_string(self):
        inp = '"Hello, World!'
        expected = [hulk_grammar.string_literal, hulk_grammar.G.EOF]
        tokens, errors = lexer(inp)
        gotten = [token.token_type for token in tokens]
        self.assertNotEqual(expected, gotten)
        self.assertEqual(len(errors), 1, f"Expects 1 errors, but got {len(errors)}")

    def test_boolean(self):
        inp = 'true false'
        expected = [hulk_grammar.bool_literal, hulk_grammar.bool_literal, hulk_grammar.G.EOF]
        tokens, errors = lexer(inp)
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_boolean_with_string(self):
        inp = 'true "false"'
        expected = [hulk_grammar.bool_literal, hulk_grammar.string_literal, hulk_grammar.G.EOF]
        tokens, errors = lexer(inp)
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_id_starting_with_boolean(self):
        inp = 'trueajabsj  falsejhsd'
        expected = [hulk_grammar.idx, hulk_grammar.idx, hulk_grammar.G.EOF]
        tokens, errors = lexer(inp)
        gotten = [token.token_type for token in tokens]
        self.assertEqual(expected, gotten)
        self.assertEqual(len(errors), 0, f"Expects {0} errors, but got {len(errors)}")


if __name__ == '__main__':
    unittest.main()
