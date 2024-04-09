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


class TestHulkAll(unittest.TestCase):

    def test_all_1(self):
        inp = (''' 
                type Person(){
                    name = "John";
                    age = 25;
                    
                    printName(){
                        print(name);
                    }
                }
                
                let x = new Person() in x.printNam();
        ''')
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(2, len(errors))

    def test___(self):
        inp = (''' 
                type Person(){
                    name = "John";
                    age = 25;

                    printName(){
                        print(self.name);
                    }
                }

                let x = new Person() in x.printName();
        ''')
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors))

    def test____(self):
        inp = (''' 
                       type Person(){
                            name = "John";
                            age = 25;
                            
                           printName(){
                                print(name);
                            }
                        }
                        
                        let x = new Person() in if (x.name == "Jane") print("Jane") else print("John");
               ''')
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(2, len(errors))

    def test_____(self):
        inp = (''' 
                       type Person(){
                            name = "John";
                            age = 25;

                           printName(){
                                print(self.name);
                            }
                        }

                        let x = new Person() in if ("Jane" == "Hola") print("Jane") else print("John");
               ''')
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors))

    def test_suc_min_sort(self):
        inp = '''
            function Sort(A) => 
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

            print(Sort([78, 12, 100, 0, 6, 9, 4.5]));
        '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors))

    def testLeastCommonSubsequence(self):
        inp = '''
            function Max(a,b) => if (a > b) a else b;
            function MaxSumSubarray(A) =>
                let MaxAccum = 0 , Actual = 0 in 
                    for (i in A)
                    {
                        Actual := Max(0, Actual + i);
                        MaxAccum := Max(Actual, MaxAccum);
                    };

            MaxSumSubarray([5,7,3,8,2]);
            
              '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors))

    def testLeastCommonSubsequence1(self):
        inp = '''
            function Max(a,b) => if (a > b) a else b;
            function MaxSumSubarray(A: Number[]) =>
                let MaxAccum = 0 , Actual = 0 in 
                    for (i in A)
                    {
                        Actual := Max(0, Actual + i);
                        MaxAccum := Max(Actual, MaxAccum);
                    };

            MaxSumSubarray([5,7,3,8,2]);

              '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors))

    def testIsPrime(self):
        inp = '''
        function IsPrime(n) => let a = false in for(i in range(2,sqrt(n)))
        if(n % i == 0) a := true else a;
        IsPrime(23);
        '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors))

    def testIsPrime_(self):
        inp = '''
           function IsPrime(n) => let a = false in for(i in range(2,sqrt(n)))
           if(n % i == 0) a := true else a;
           IsPrime(23);
           '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors))

    def test_lcm(self):
        inp = '''
            function gcd(a, b) => if (a % b == 0) b else gcd(b, a % b);
            function lcm(a, b) => a * b / gcd(a,b);
            lcm(13,15);
        '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors))

    def test_lcm_1(self):
        inp = '''
           function gcd(a,b): Number => if (a % b == 0) b else gcd(b, a % b);
           function lcm(a,b) => a * b / gcd(a,b);
           lcm(13,15);
       '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors))

    def test_recursive_gcd(self):
        inp = '''
               function gcd(a,b) => if (a % b == 0) b else gcd(b, a % b);
               gcd(13,15);
               '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors))

    def test_recursive_gcd1(self):
        inp = '''
               function gcd(a,b): Number => if (a % b == 0) b else gcd(b, a % b);
               gcd(13,15);
               '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors))

    def test_(self):
        inp = '''
                 type D {
                    getc() => while(false) 5;      
                }
                                   
                if(let a = new D() in true)
                    print(a.getc())
                else
                    1;
                  '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors))

    def test__(self):
        inp = '''
                    type D {
                        getc() => while(false) 5;
                        equals() => true;
                    }
                                       
                    let a = new D() in
                        print(a.getc());
                     '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors))

    def test_______(self):
        inp = '''
            function f(x: Object) => x;
            let x: Iterable = new Range(1, 3) in f(x);
            '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors))

    def test___(self):
        inp = '''
            function f(x: Number) => x;
            let x: Iterable = new Range(1, 3) in f(x);
            '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors))

    def test______(self):
        inp = '''
            type A inherits B {
                x = x;
                y = y;
            }
            type B (x, y) {
                x = x + y;
            }
            5;
        '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(0, len(errors))

    def test_____(self):
        inp = '''
               type A inherits B {
                   x = x;
                   y = y;
               }
               type B (x, y) inherits A {
                   x = x + y;
               }
               5;
           '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors))

    def test_________(self):
        inp = '''
                type A inherits B {
                    x = x;
                    y = y;
                }
                
                type B inherits C {
                    x = x;
                    y = y;
                }
                
                type C (x, y) {
                    x = x + y | y;
                    y = y;
                }
                
                5;
            '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors))

    def test___________(self):
        inp = '''
                type C (x, y) {
                    x = x + y;
                    y = y | y;
                }
                5;
            '''
        ast, errors, context, scope = run_code(inp, True)
        self.assertEqual(1, len(errors))
