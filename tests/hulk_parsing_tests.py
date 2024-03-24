import unittest

from src.hulk_grammar.hulk_grammar import G
from src.lexer.hulk_lexer import HulkLexer
from src.parsing import LR1Parser

lexer = HulkLexer()
parser = LR1Parser(G)


class Parsing(unittest.TestCase):

    def test(self):
        self.assertTrue(True, "Should be True")


if __name__ == '__main__':
    unittest.main()
