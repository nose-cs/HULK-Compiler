import unittest

from src.lexer.hulk_lexer import HulkLexer

lexer = HulkLexer()


class TestHulkFunctions(unittest.TestCase):

    def test_invalid_syntax_function(self):
        inp = 'function operate(x, y) => {\nprint(x + y);\n}'
        expected = []
        gotten = []
        self.assertEqual(expected, gotten)


if __name__ == '__main__':
    unittest.main()
