import unittest
from tests.assertt_without_exception import assert_without_exception
from src.lexer.hulk_lexer import HulkLexer
from src.parsing import LR1Parser
lexer = HulkLexer()
parser = LR1Parser()

class TestHulkFLoops(unittest.TestCase):

    def test_while_loop_in_let(self):
        inp = 'let a = 10 in while (a >= 0) { print(a); a := a - 1;}'
        tokens = lexer._tokenize(inp)
        return assert_without_exception(parser, tokens)

    def loop_in_function(self):
        inp = '''
    function gcd(a, b) => while (a > 0)
    let m = a % b in {
        b := a;
        a := m;
    };
    gcd(5,6);
    '''
        tokens = lexer._tokenize(inp)
        return assert_without_exception(parser, tokens)

    def test_while_loop_in_let(self):
        inp = 'for (x in range(0, 10)) print(x);'
        tokens = lexer._tokenize(inp)
        return assert_without_exception(parser, tokens)
    
    def explicit_form_of_for(self):
        inp = '''
    let iterable = range(0, 10) in
    while (iterable.next())
        let x = iterable.current() in
            print(x);
    '''
        tokens = lexer._tokenize(inp)
        return assert_without_exception(parser, tokens)
    

if __name__ == '__main__':
    unittest.main()