import unittest
from tests.assertt_without_exception import assert_without_exception
from src.lexer.hulk_lexer import HulkLexer
from src.parsing import LR1Parser
lexer = HulkLexer()
parser = LR1Parser()

class TestConditionals(unittest.TestCase):

    def test_Basic_ifelse(self):
        inp = 'let a = 42 in if (a % 2 == 0) print("Even") else print("odd");'
        tokens = lexer._tokenize(inp)
        return assert_without_exception(parser, tokens)

    def conditional_inside_print(self):
        inp = '''
    let a = 42 in print(if (a % 2 == 0) "even" else "odd");
    '''
        tokens = lexer._tokenize(inp)
        return assert_without_exception(parser, tokens)

    def expblock(self):
        inp = '''
            let a = 42 in
    if (a % 2 == 0) {
        print(a);
        print("Even");
    }
    else print("Odd");
        '''
        tokens = lexer._tokenize(inp)
        return assert_without_exception(parser, tokens)
    
    def multibranch(self):
        inp = '''
    let a = 42 in let mod = a % 3 in
    print(
        if (mod == 0) "Magic"
        elif (mod % 3 == 1) "Woke"
        else "Dumb"
    );

    '''
        tokens = lexer._tokenize(inp)
        return assert_without_exception(parser, tokens)