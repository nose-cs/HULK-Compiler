import unittest

from src.evaluation import evaluate_reverse_parse
from src.lexer.hulk_lexer import HulkLexer
from src.parser.hulk_parser import HulkParser
from src.semantics.semantic_analysis_pipeline import semantic_analysis_pipeline

lexer = HulkLexer()
parser = HulkParser()


def run_code(inp: str, debug=False):
    tokens, errors = lexer(inp)
    assert not errors
    derivation, operations, errors = parser(tokens)
    print(errors)
    assert not errors
    ast = evaluate_reverse_parse(derivation, operations, tokens)
    ast, errors, context, scope = semantic_analysis_pipeline(ast, debug)
    return ast, errors, context, scope


class TestHulkVectors(unittest.TestCase):

    def test_while_loop_in_let_in(self):
        inp = ('''
        for (x in [5, 6,7])
            print(x);
            ''')
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")

    def test_while_in_method(self):
        inp = '''
        for (x in ["hola", 9])
            print(x);
        '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")

    def test_while_in_method_(self):
        inp = '''
           for (x in [9 + "hola"]) print(x);
           '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors), f"Expects 1 error, but got {len(errors)}")

    def test__(self):
        inp = '''
           for (x in [9 + 3, 50]) x[4] := 8;
           '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors), f"Expects 1 error, but got {len(errors)}")

    def test___(self):
        inp = '''
           let x = [1,2,3] in x[7] := 4;
           '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")

    def test_force_object_return(self):
        inp = '''
           let x: Iterable = [1,2,3] in x[7] + 10;
           '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors), f"Expects 1 error, but got {len(errors)}")

    def test_force_(self):
        inp = '''
           let x = 5 + "20" in x[7] + 10;
           '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors), f"Expects 1 error, but got {len(errors)}")

    def test_invalid_assigment(self):
        inp = '''
           let x = [7,8,9] in x := [new Object()];
           '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors), f"Expects 1 error, but got {len(errors)}")

    def test_valid_assigment(self):
        inp = '''
              let x = ["casa", 7, 8] in x := ["hola"];
              '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")

    def test_is_prime(self):
        inp = '''
            function IsPrime(n) => let a = false in for(i in range(2,sqrt(n)))
                if(n % i == 0) a := true else a;
            IsPrime(23);
            '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")

    def test_____(self):
        inp = '''
            let a = [78, 12, 100, 0, 6, 9, 4.5] in
            {
                print(a.size());
            }
            '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")

    def test_param_type(self):
        inp = ('''
           function Sort(A: Number[]) => 
            let  aux = 0 in for (i in range(0, A.size()))
                for (j in range(i, A.size()))
                 if(A[j] < A[i])
                 {
                    aux := A[i];
                    A[i] := A[j];
                    A[j] := aux;
                    A;
                }
                else A;

            let a = Sort([78, 12, 100, 0, 6, 9, 4.5]) in
                {
                    print(a);
                    print(a.size());
                }
            ''')
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")

    def test_all_types(self):
        inp = ('''
           function Sort(A: Number[]): Number[] => 
            let  aux = 0 in for (i in range(0, A.size()))
                for (j in range(i, A.size()))
                 if(A[j] < A[i])
                 {
                    aux := A[i];
                    A[i] := A[j];
                    A[j] := aux;
                    A;
                }
                else A;

            let a: Number[] = Sort([78, 12, 100, 0, 6, 9, 4.5]) in
                {
                    print(a);
                    print(a.size());
                }
            ''')
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")
