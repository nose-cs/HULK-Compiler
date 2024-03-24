import unittest

from src.lexer.hulk_lexer import HulkLexer

lexer = HulkLexer()


class TestLexicographicHulk(unittest.TestCase):

    # ---------------------------------------------Expressions------------------------------------------------#

    def test_number(self):
        expected = '[<number>: 42 (1, 1), ;: ; (1, 3), $: $ (2, 0)]'
        tokens, errors = lexer('42;')
        gotten = str(tokens)
        self.assertEqual(expected, gotten, f"Expects {expected}, but got {gotten}")
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_print(self):
        expected = '[<id>: print (1, 1), (: ( (1, 6), <number>: 42 (1, 7), ): ) (1, 9), ;: ; (1, 10), $: $ (2, 0)]'
        tokens, errors = lexer('print(42);')
        gotten = str(tokens)
        self.assertEqual(expected, gotten, f"Expects {expected}, but got {gotten}")
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_string(self):
        expected = '[<id>: print (1, 1), (: ( (1, 6), <string>: "The message is "Hello World"" (1, 7), ): ) (1, 37), ;: ; (1, 38), $: $ (2, 0)]'
        tokens, errors = lexer('print("The message is \"Hello World\"");')
        gotten = str(tokens)
        self.assertEqual(expected, gotten, f"Expects {expected}, but got {gotten}")
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_concat(self):
        expected = '[<id>: print (1, 1), (: ( (1, 6), <string>: "The meaning of life is " (1, 7), @: @ (1, 33), <number>: 42 (1, 35), ): ) (1, 37), ;: ; (1, 38), $: $ (2, 0)]'
        tokens, errors = lexer('print("The meaning of life is " @ 42);')
        gotten = str(tokens)
        self.assertEqual(expected, gotten, f"Expects {expected}, but got {gotten}")
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test5_built_in(self):
        expected = '[<id>: print (1, 1), (: ( (1, 6), <id>: sin (1, 7), (: ( (1, 10), <number>: 2 (1, 11), *: * (1, 13), <id>: PI (1, 15), ): ) (1, 17), ^: ^ (1, 19), <number>: 2 (1, 21), +: + (1, 23), <id>: cos (1, 25), (: ( (1, 28), <number>: 3 (1, 29), *: * (1, 31), <id>: PI (1, 33), /: / (1, 36), <id>: log (1, 38), (: ( (1, 41), <number>: 4 (1, 42), ,: , (1, 43), <number>: 64 (1, 45), ): ) (1, 47), ): ) (1, 48), ): ) (1, 49), ;: ; (1, 50), $: $ (2, 0)]'
        tokens, errors = lexer('print(sin(2 * PI) ^ 2 + cos(3 * PI / log(4, 64)));')
        gotten = str(tokens)
        self.assertEqual(expected, gotten, f"Expects {expected}, but got {gotten}")
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    def test_block(self):
        tokens, errors = lexer('{\nprint(42);\n print(sin(PI/2));\n print("Hello World");\n}')
        gotten = len(tokens)
        self.assertEqual(23, gotten, f"Expects {23} token, but got {gotten}")
        self.assertEqual(len(errors), 0, f"Expects 0 errors, but got {len(errors)}")

    # ---------------------------------------------Functions------------------------------------------------#

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

        # ---------------------------------------------Variables------------------------------------------------#

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
