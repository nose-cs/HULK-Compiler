import unittest

from src.lexer.hulk_lexer import HulkLexer

lexer = HulkLexer()


class TestHulkFunctions(unittest.TestCase):

    def test_function(self):
        expected = '[function: function (1, 1), <id>: tan (1, 10), (: ( (1, 13), <id>: x (1, 14), ): ) (1, 15), =>: => (1, 17), <id>: sin (1, 20), (: ( (1, 23), <id>: x (1, 24), ): ) (1, 25), /: / (1, 27), <id>: cos (1, 29), (: ( (1, 32), <id>: x (1, 33), ): ) (1, 34), ;: ; (1, 35), $: $ (2, 0)]'
        tokens, errors = lexer('function tan(x) => sin(x) / cos(x);')
        gotten = str(tokens)
        self.assertEqual(expected, gotten, f"Expects {expected}, but got {gotten}")
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_functions_and_expression(self):
        tokens, errors = lexer(
            'function cot(x) => 1 / tan(x);\nfunction tan(x) => sin(x) / cos(x);\nprint(tan(PI) ** 2 + cot(PI) ** 2);')
        gotten = len(tokens)
        self.assertEqual(47, gotten, f"Expects {47} token, but got {gotten}")
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_full_form_function(self):
        inp = 'function operate(x, y) {\nprint(x + y);\nprint(x - y);\nprint(x * y);\nprint(x / y);\n}'
        expected = '[function: function (1, 1), <id>: operate (1, 10), (: ( (1, 17), <id>: x (1, 18), ,: , (1, 19), <id>: y (1, 21), ): ) (1, 22), {: { (1, 24), <id>: print (2, 1), (: ( (2, 6), <id>: x (2, 7), +: + (2, 9), <id>: y (2, 11), ): ) (2, 12), ;: ; (2, 13), <id>: print (3, 1), (: ( (3, 6), <id>: x (3, 7), -: - (3, 9), <id>: y (3, 11), ): ) (3, 12), ;: ; (3, 13), <id>: print (4, 1), (: ( (4, 6), <id>: x (4, 7), *: * (4, 9), <id>: y (4, 11), ): ) (4, 12), ;: ; (4, 13), <id>: print (5, 1), (: ( (5, 6), <id>: x (5, 7), /: / (5, 9), <id>: y (5, 11), ): ) (5, 12), ;: ; (5, 13), }: } (6, 1), $: $ (7, 0)]'
        tokens, errors = lexer(inp)
        gotten = str(tokens)
        self.assertEqual(expected, gotten, f"Expects {expected}, but got {gotten}")
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_invalid_syntax_function(self):
        inp = 'function operate(x, y) => {\nprint(x + y);\n}'
        expected = '[function: function (1, 1), <id>: operate (1, 10), (: ( (1, 17), <id>: x (1, 18), ,: , (1, 19), <id>: y (1, 21), ): ) (1, 22), =>: => (1, 24), {: { (1, 27), <id>: print (2, 1), (: ( (2, 6), <id>: x (2, 7), +: + (2, 9), <id>: y (2, 11), ): ) (2, 12), ;: ; (2, 13), }: } (3, 1), $: $ (4, 0)]'
        tokens, errors = lexer(inp)
        gotten = str(tokens)
        self.assertEqual(expected, gotten, f"Expects {expected}, but got {gotten}")
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")


if __name__ == '__main__':
    unittest.main()
