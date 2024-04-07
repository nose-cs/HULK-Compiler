import unittest

from src.evaluation import evaluate_reverse_parse
from src.lexer.hulk_lexer import HulkLexer
from src.parser.hulk_parser import HulkParser
from src.semantics.semantic_analysis_pipeline import semantic_analysis_pipeline

lexer = HulkLexer()
parser = HulkParser()


def run_code(inp: str, debug=False):
    tokens, errors = lexer(inp)
    if errors:
        print(errors)
    assert not errors
    derivation, operations, errors = parser(tokens)
    if errors:
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

    def test_vector_comp(self):
        inp = ('''
            function square(x: Number) => [i ^ 2 || i in range(1, x)];

            let b = 4 in {
                let a = square(5) in a[2] := 4;
                let a = 5 in {
                    if (a == 5) for (i in square(b)) print(i)
                    else print("Hello World");
                };
            }
            ''')
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")

    def test____(self):
        inp = ('''
            function square(x: Number) => [i ^ 2 || i in ra(1, x)];

            let b = 4 in {
                let a = square(5) in a[2] := 4;
                let a = 5 in {
                    if (a == 5) for (i in square(b)) print(i)
                    else print("Hello World");
                };
            }
            ''')
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors), f"Expects 1 error, but got {len(errors)}")

    def test_error_type(self):
        inp = ('''
            function square(x: Number) => [9, "hola", 9 + "hola"];

            let b = 4 in {
                let a = square(5) in a[2] := 4;
                let a = 5 in {
                    if (a == 5) for (i in square(b)) print(i)
                    else print("Hello World");
                };
            }
            ''')
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors), f"Expects 1 error, but got {len(errors)}")

    def test_________________(self):
        inp = ('''
            function square(x) => let a = new B() in [i ^ 2 || i in a.f(x)];
            
            type B {
                f(x) => let a = new A() in [i ^ 2 || i in a.f(x)];
            }
            
            type A {
                f(x: Number) => [i || i in range(1, x)];
            }

            let b = 4 in {
                let a = square(5) in a[2] := 4;
                let a = 5 in {
                    if (a == 5) for (i in square(b)) print(i)
                    else print("Hello World");
                };
            }
            ''')
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")

    def test_bidimensional_vector(self):
        inp = ('''
                function f(x: Number[][]) =>  [[i ^ 2 || i in a] || a in x];

                let b = f([[0,1,2],[0,1,2]]) in print(b);
                ''')
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")

    def test________________(self):
        inp = ('''
                function f(x) => g(x);
                function g(x) => x + x;
                f(5);
                ''')
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")

    def test______________________(self):
        inp = ('''
                   function fact(x) => let f = 1 in for (i in range(1, x+1)) f := f * i;
                   fact(6);
                   ''')
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors), f"Expects 0 error, but got {len(errors)}")
