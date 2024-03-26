import src.hulk_grammar.hulk_grammar as hulk_grammar
from src.errors import LexicographicError
from src.hulk_grammar.hulk_grammar import G
from src.lexer.lexer import Lexer
from src.pycompiler import Terminal
import dill
import sys

nonzero_digits = '|'.join(str(n) for n in range(1, 10))
digits = '|'.join(str(n) for n in range(10))
lower_letters = '|'.join(chr(n) for n in range(ord('a'), ord('z') + 1))
upper_letters = '|'.join(chr(n) for n in range(ord('A'), ord('Z') + 1))

operators = [
    ("{", hulk_grammar.obracket), ("}", hulk_grammar.cbracket), (";", hulk_grammar.semicolon),
    ("\\(", hulk_grammar.opar), ("\\)", hulk_grammar.cpar), ("=>", hulk_grammar.arrow), (",", hulk_grammar.comma),
    ("=", hulk_grammar.equal), (":=", hulk_grammar.dest_eq),
    ("+", hulk_grammar.plus), ("-", hulk_grammar.minus), ("\\*", hulk_grammar.star), ("/", hulk_grammar.div),
    ("^", hulk_grammar.power), ("%", hulk_grammar.mod), ("\\*\\*", hulk_grammar.power2),
    ("==", hulk_grammar.eq), ("!=", hulk_grammar.neq), ("<=", hulk_grammar.leq), (">=", hulk_grammar.geq),
    ("<", hulk_grammar.lt), (">", hulk_grammar.gt), ("&", hulk_grammar.and_op), ("\\|", hulk_grammar.or_op),
    ("!", hulk_grammar.not_op), ("@", hulk_grammar.amper), ("@@", hulk_grammar.double_amp), (".", hulk_grammar.dot),
    (":", hulk_grammar.colon), ("\\|\\|", hulk_grammar.double_bar), ("\\[", hulk_grammar.o_square_bracket),
    ("\\]", hulk_grammar.c_square_bracket)]

reserved_words = [("let", hulk_grammar.let), ("in", hulk_grammar.in_),
                  ("if", hulk_grammar.if_), ("else", hulk_grammar.else_), ("elif", hulk_grammar.elif_),
                  ("while", hulk_grammar.while_), ("for", hulk_grammar.for_),
                  ("function", hulk_grammar.function),
                  ("new", hulk_grammar.new), ("is", hulk_grammar.is_), ("as", hulk_grammar.as_),
                  ("protocol", hulk_grammar.protocol), ("extends", hulk_grammar.extends),
                  ("type", hulk_grammar.word_type), ("inherits", hulk_grammar.inherits),
                  ("true|false", hulk_grammar.bool_term)]

# tokens that don't have any syntactic meaning
spaces = Terminal("<spaces>", None)
escaped_char = Terminal("<escaped_char>", None)
unterminated_string = Terminal("<unterminated_string>", None)

# tokens that we are going to look for to recover of an unknown token error
synchronizing_tokens = [("  *", spaces), ("\n|\t", escaped_char)] + operators

# tokens that we are going to use to build the lexer
hulk_tokens = operators + reserved_words + [
    ('|'.join([f"({nonzero_digits})({digits})*",
               f"({nonzero_digits})({digits})*.({digits})({digits})*",
               f"0.({digits})({digits})*",
               "0"]), hulk_grammar.number),
    (f"(_|{upper_letters}|{lower_letters})(_|{upper_letters}|{lower_letters}|{digits})*", hulk_grammar.idx),
    (
        "\"(\x00|\x01|\x02|\x03|\x04|\x05|\x06|\x07|\x08|\t|\n|\x0b|\x0c|\r|\x0e|\x0f|\x10|\x11|\x12|\x13|\x14|\x15|\x16|\x17|\x18|\x19|\x1a|\x1b|\x1c|\x1d|\x1e|\x1f| |!|#|$|%|&|\'|\\(|\\)|\\*|+|,|-|.|/|0|1|2|3|4|5|6|7|8|9|:|;|<|=|>|?|@|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|[|\\\\|]|^|_|`|a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|{|\\||}|~|\x7f|\x80|\x81|\x82|\x83|\x84|\x85|\x86|\x87|\x88|\x89|\x8a|\x8b|\x8c|\x8d|\x8e|\x8f|\x90|\x91|\x92|\x93|\x94|\x95|\x96|\x97|\x98|\x99|\x9a|\x9b|\x9c|\x9d|\x9e|\x9f|\xa0|¡|¢|£|¤|¥|¦|§|¨|©|ª|«|¬|\xad|®|¯|°|±|²|³|´|µ|¶|·|¸|¹|º|»|¼|½|¾|¿|À|Á|Â|Ã|Ä|Å|Æ|Ç|È|É|Ê|Ë|Ì|Í|Î|Ï|Ð|Ñ|Ò|Ó|Ô|Õ|Ö|×|Ø|Ù|Ú|Û|Ü|Ý|Þ|ß|à|á|â|ã|ä|å|æ|ç|è|é|ê|ë|ì|í|î|ï|ð|ñ|ò|ó|ô|õ|ö|÷|ø|ù|ú|û|ü|ý|þ|ÿ)*\"",
        hulk_grammar.str_term),
    ("  *", spaces),
    (
        "\"(\x00|\x01|\x02|\x03|\x04|\x05|\x06|\x07|\x08|\t|\n|\x0b|\x0c|\r|\x0e|\x0f|\x10|\x11|\x12|\x13|\x14|\x15|\x16|\x17|\x18|\x19|\x1a|\x1b|\x1c|\x1d|\x1e|\x1f| |!|#|$|%|&|\'|\\(|\\)|\\*|+|,|-|.|/|0|1|2|3|4|5|6|7|8|9|:|;|<|=|>|?|@|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|[|\\\\|]|^|_|`|a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|{|\\||}|~|\x7f|\x80|\x81|\x82|\x83|\x84|\x85|\x86|\x87|\x88|\x89|\x8a|\x8b|\x8c|\x8d|\x8e|\x8f|\x90|\x91|\x92|\x93|\x94|\x95|\x96|\x97|\x98|\x99|\x9a|\x9b|\x9c|\x9d|\x9e|\x9f|\xa0|¡|¢|£|¤|¥|¦|§|¨|©|ª|«|¬|\xad|®|¯|°|±|²|³|´|µ|¶|·|¸|¹|º|»|¼|½|¾|¿|À|Á|Â|Ã|Ä|Å|Æ|Ç|È|É|Ê|Ë|Ì|Í|Î|Ï|Ð|Ñ|Ò|Ó|Ô|Õ|Ö|×|Ø|Ù|Ú|Û|Ü|Ý|Þ|ß|à|á|â|ã|ä|å|æ|ç|è|é|ê|ë|ì|í|î|ï|ð|ñ|ò|ó|ô|õ|ö|÷|ø|ù|ú|û|ü|ý|þ|ÿ)*",
        unterminated_string),
    ("\n|\t", escaped_char),
]


class HulkLexer(Lexer):
    def __init__(self, rebuild=False, convert_to_dfa=False, save=False) -> None:
        super().__init__(hulk_tokens, G.EOF, rebuild, convert_to_dfa, synchronizing_tokens)

        if not rebuild:
            try:
                with open('src/lexer/hulk_lexer.pkl', 'rb') as automaton_pkl:
                    self.automaton = dill.load(automaton_pkl)
                with open('src/lexer/hulk_lexer_synchronizing.pkl', 'rb') as synchronizing_automaton_pkl:
                    self.synchronizing_automaton = dill.load(synchronizing_automaton_pkl)
            except:
                super().__init__(hulk_tokens, G.EOF, True, convert_to_dfa, synchronizing_tokens)

        if save:
            sys.setrecursionlimit(10000)

            with open('src/lexer/hulk_lexer.pkl', 'wb') as automaton_pkl:
                dill.dump(self.automaton, automaton_pkl)
            with open('src/lexer/hulk_lexer_synchronizing.pkl', 'wb') as synchronizing_automaton_pkl:
                dill.dump(self.synchronizing_automaton, synchronizing_automaton_pkl)

    @staticmethod
    def find_errors(tokens):
        errors = []
        for token in tokens:
            if not token.is_valid:
                errors.append(LexicographicError(LexicographicError.UNKNOWN_TOKEN, token.row, token.column))
            if token.token_type == unterminated_string.Name:
                errors.append(LexicographicError(LexicographicError.UNTERMINATED_STRING, token.row, token.column))
        return errors

    def __call__(self, text):
        tokens = super().__call__(text)
        errors = self.find_errors(tokens)
        return [token for token in tokens if
                token.token_type.Name not in {spaces.Name, escaped_char.Name, unterminated_string.Name} and token.is_valid], errors
