import unittest

from src.lexer.hulk_lexer import HulkLexer

lexer = HulkLexer()


class TestHulkVariables(unittest.TestCase):
    def test_let_in(self):
        inp = 'let msg = "Hello World" in print(msg);'
        expected = '[let: let (1, 1), <id>: msg (1, 5), =: = (1, 9), <string>: "Hello World" (1, 11), in: in (1, 25), <id>: print (1, 28), (: ( (1, 33), <id>: msg (1, 34), ): ) (1, 37), ;: ; (1, 38), $: $ (2, 0)]'
        tokens, errors = lexer(inp)
        gotten = str(tokens)
        self.assertEqual(expected, gotten, f"Expects {expected}, but got {gotten}")
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    # semantic equivalent
    def test_let_in_with_2_vars(self):
        inp = 'let number = 42, text = "The meaning of life is" in print(text @ number);'
        expected = '[let: let (1, 1), <id>: number (1, 5), =: = (1, 12), <number>: 42 (1, 14), ,: , (1, 16), <id>: text (1, 18), =: = (1, 23), <string>: "The meaning of life is" (1, 25), in: in (1, 50), <id>: print (1, 53), (: ( (1, 58), <id>: text (1, 59), @: @ (1, 64), <id>: number (1, 66), ): ) (1, 72), ;: ; (1, 73), $: $ (2, 0)]'
        tokens, errors = lexer(inp)
        gotten = str(tokens)
        self.assertEqual(expected, gotten, f"Expects {expected}, but got {gotten}")
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_let_in_with_2_vars_but_nested(self):
        inp = 'let number = 42 in let text = "The meaning of life is" in print(text @ number);'
        tokens, errors = lexer(inp)
        gotten = len(tokens)
        self.assertEqual(18, gotten, f"Expects {18}, but got {gotten}")
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_let_in_with_2_vars_but_associative(self):
        inp = 'let number = 42 in (let text = "The meaning of life is" in (print(text @ number)) );'
        tokens, errors = lexer(inp)
        gotten = len(tokens)
        self.assertEqual(22, gotten, f"Expects {22}, but got {gotten}")
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_let_in_block(self):
        inp = 'let a = 5, b = 10, c = 20 in {\nprint(a+b);\nprint(b*c);\nprint(c/a);\n}'
        tokens, errors = lexer(inp)
        gotten = len(tokens)
        self.assertEqual(37, gotten, f"Expects {37}, but got {gotten}")
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")


if __name__ == '__main__':
    unittest.main()
