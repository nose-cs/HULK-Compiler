import unittest

from src.lexer.hulk_lexer import HulkLexer
from src.parsing import LR1Parser
from tests.assertt_without_exception import assert_without_exception

lexer = HulkLexer()
parser = LR1Parser()


class TestMiscelaneous(unittest.TestCase):

    def recursive_gcd(self):
        inp = '''
            function gcd(a,b) => if (a % b == 0) b else gcd(b, a % b);
            gcd(13,15);
            '''
        tokens = lexer._tokenize(inp)
        return assert_without_exception(parser, tokens)

    def lcm(self):
        inp = '''
        function gcd(a,b) => if (a % b == 0) b else gcd(b, a % b);
        function lcm(a,b) => a * b / gcd(a,b);
        lcm(13,15);
        
    '''
        tokens = lexer._tokenize(inp)
        return assert_without_exception(parser, tokens)

    def IsPrime(self):
        inp = '''
        function IsPrime(n) => let a = false in for(i in range(2,sqrt(n)))
        if(n % i == 0) a := true else a;
        IsPrime(23);
        '''
        tokens = lexer._tokenize(inp)
        return assert_without_exception(parser, tokens)

    def LeastCommonSubsequence(self):
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
        tokens = lexer._tokenize(inp)
        return assert_without_exception(parser, tokens)

    def sucesiveMinsOrd(self):
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
