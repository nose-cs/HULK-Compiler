import src.hulk_grammar.hulk_grammar as hulk_grammar
from src.errors import LexicographicError
from src.hulk_grammar.hulk_grammar import G
from src.lexer.lexer import Lexer
from src.pycompiler import Terminal

nonzero_digits = '|'.join(str(n) for n in range(1, 10))
digits = '|'.join(str(n) for n in range(10))
lower_letters = '|'.join(chr(n) for n in range(ord('a'), ord('z') + 1))
upper_letters = '|'.join(chr(n) for n in range(ord('A'), ord('Z') + 1))

number_regexes = [f"(({nonzero_digits})({digits})*)",
                  f"(({nonzero_digits})({digits})*(.)({digits})*)",
                  f"((0.)({digits})*)",
                  "(0)"]
spaces = Terminal("<spaces>", None)
unterminated_string = Terminal("<unterminated_string>", None)

Regex_Terminal = [
    ("{", hulk_grammar.obracket), ("}", hulk_grammar.cbracket), (";", hulk_grammar.semicolon),
    ("\\(", hulk_grammar.opar), ("\\)", hulk_grammar.cpar), ("=>", hulk_grammar.arrow), (",", hulk_grammar.comma),
    ("let", hulk_grammar.let), ("in", hulk_grammar.in_), ("=", hulk_grammar.equal), (":=", hulk_grammar.dest_eq),
    ("if", hulk_grammar.if_), ("else", hulk_grammar.else_), ("elif", hulk_grammar.elif_),
    ("while", hulk_grammar.while_), ("for", hulk_grammar.for_), ("function", hulk_grammar.function),
    ("+", hulk_grammar.plus), ("-", hulk_grammar.minus), ("\\*", hulk_grammar.star), ("/", hulk_grammar.div),
    ("^", hulk_grammar.power), ("%", hulk_grammar.mod), ("\\*\\*", hulk_grammar.power2),
    ("==", hulk_grammar.eq), ("!=", hulk_grammar.neq), ("<=", hulk_grammar.leq), (">=", hulk_grammar.geq),
    ("<", hulk_grammar.lt), (">", hulk_grammar.gt), ("&", hulk_grammar.and_op), ("\\|", hulk_grammar.or_op),
    ("!", hulk_grammar.not_op), ("(true)|(false)", hulk_grammar.bool_term), ("@", hulk_grammar.amper),
    ("@@", hulk_grammar.double_amp), ('|'.join(number_regexes), hulk_grammar.number), (".", hulk_grammar.dot),
    (":", hulk_grammar.colon),
    (f"((_|{upper_letters}|{lower_letters})(_|{upper_letters}|{lower_letters}|{digits})*)", hulk_grammar.idx),
    (
        "\"(\x00|\x01|\x02|\x03|\x04|\x05|\x06|\x07|\x08|\t|\n|\x0b|\x0c|\r|\x0e|\x0f|\x10|\x11|\x12|\x13|\x14|\x15|\x16|\x17|\x18|\x19|\x1a|\x1b|\x1c|\x1d|\x1e|\x1f| |!|#|$|%|&|\'|\\(|\\)|\\*|+|,|-|.|/|0|1|2|3|4|5|6|7|8|9|:|;|<|=|>|?|@|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|[|\\\\|]|^|_|`|a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|{|\\||}|~|\x7f|\x80|\x81|\x82|\x83|\x84|\x85|\x86|\x87|\x88|\x89|\x8a|\x8b|\x8c|\x8d|\x8e|\x8f|\x90|\x91|\x92|\x93|\x94|\x95|\x96|\x97|\x98|\x99|\x9a|\x9b|\x9c|\x9d|\x9e|\x9f|\xa0|¡|¢|£|¤|¥|¦|§|¨|©|ª|«|¬|\xad|®|¯|°|±|²|³|´|µ|¶|·|¸|¹|º|»|¼|½|¾|¿|À|Á|Â|Ã|Ä|Å|Æ|Ç|È|É|Ê|Ë|Ì|Í|Î|Ï|Ð|Ñ|Ò|Ó|Ô|Õ|Ö|×|Ø|Ù|Ú|Û|Ü|Ý|Þ|ß|à|á|â|ã|ä|å|æ|ç|è|é|ê|ë|ì|í|î|ï|ð|ñ|ò|ó|ô|õ|ö|÷|ø|ù|ú|û|ü|ý|þ|ÿ)*\"",
        hulk_grammar.str_term),
    ("  *", spaces),
    (
        "\"(\x00|\x01|\x02|\x03|\x04|\x05|\x06|\x07|\x08|\t|\n|\x0b|\x0c|\r|\x0e|\x0f|\x10|\x11|\x12|\x13|\x14|\x15|\x16|\x17|\x18|\x19|\x1a|\x1b|\x1c|\x1d|\x1e|\x1f| |!|#|$|%|&|\'|\\(|\\)|\\*|+|,|-|.|/|0|1|2|3|4|5|6|7|8|9|:|;|<|=|>|?|@|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|[|\\\\|]|^|_|`|a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|{|\\||}|~|\x7f|\x80|\x81|\x82|\x83|\x84|\x85|\x86|\x87|\x88|\x89|\x8a|\x8b|\x8c|\x8d|\x8e|\x8f|\x90|\x91|\x92|\x93|\x94|\x95|\x96|\x97|\x98|\x99|\x9a|\x9b|\x9c|\x9d|\x9e|\x9f|\xa0|¡|¢|£|¤|¥|¦|§|¨|©|ª|«|¬|\xad|®|¯|°|±|²|³|´|µ|¶|·|¸|¹|º|»|¼|½|¾|¿|À|Á|Â|Ã|Ä|Å|Æ|Ç|È|É|Ê|Ë|Ì|Í|Î|Ï|Ð|Ñ|Ò|Ó|Ô|Õ|Ö|×|Ø|Ù|Ú|Û|Ü|Ý|Þ|ß|à|á|â|ã|ä|å|æ|ç|è|é|ê|ë|ì|í|î|ï|ð|ñ|ò|ó|ô|õ|ö|÷|ø|ù|ú|û|ü|ý|þ|ÿ)*",
        hulk_grammar.str_term)
]


class HulkLexer(Lexer):
    def __init__(self) -> None:
        super().__init__(Regex_Terminal, G.EOF)

    @staticmethod
    def find_errors(tokens):
        errors = []
        for token in tokens:
            if not token.is_valid:
                errors.append(LexicographicError(LexicographicError.UNKNOWN_TOKEN, token.row, token.column))
            if token.token_type is unterminated_string:
                errors.append(LexicographicError(LexicographicError.UNTERMINATED_STRING, token.row, token.column))
        return errors

    def __call__(self, text):
        tokens = super().__call__(text)
        errors = self.find_errors(tokens)
        return [token for token in tokens if
                token.token_type not in [spaces, unterminated_string] and token.is_valid], errors
