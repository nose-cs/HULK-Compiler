import unittest
from tests.assertt_without_exception import assert_without_exception
from src.lexer.hulk_lexer import HulkLexer
from src.parsing import LR1Parser
lexer = HulkLexer()
parser = LR1Parser()

class VaeDeclarations(unittest.TestCase):

    def test_Basic_ifelse(self):
        inp = 'let msg = "Hello World" in print(msg);'
        tokens = lexer._tokenize(inp)
        return assert_without_exception(parser, tokens)

    def conditional_inside_print(self):
        inp = '''
    let number = 42, text = "The meaning of life is" in
    print(text @ number);
    '''
        tokens = lexer._tokenize(inp)
        return assert_without_exception(parser, tokens)

    def expblock(self):
        inp = '''
            let number = 42 in
    let text = "The meaning of life is" in
        print(text @ number);
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