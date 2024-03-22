from src.hulk_grammar.hulk_grammar import obracket, cbracket, semicolon, opar, cpar, arrow, comma, in_, equal, \
    dest_eq, \
    if_, else_, elif_, \
    while_, for_, \
    function, \
    plus, minus, star, div, power, mod, power2, \
    eq, neq, leq, geq, gt, lt, \
    and_op, or_op, not_op, bool_term, \
    amper, double_amp, \
    str_term, number, idx, let

from src.lexer.lexer import get_lexer, get_tokens
from src.pycompiler import Terminal

nonzero_digits = '|'.join(str(n) for n in range(1, 10))
lower_letters = '|'.join(chr(n) for n in range(ord('a'), ord('z') + 1))
upper_letters = '|'.join(chr(n) for n in range(ord('A'), ord('Z') + 1))
strings_ascii_symbols = '|'.join(chr(n) for n in range(32, 257) if chr(n) not in ['"', "*", "(", ")", "|"])

Regex_Terminal = [
    ("{", obracket), ("}", cbracket), (";", semicolon), ("\\(", opar), ("\\)", cpar), ("=>", arrow), (",", comma),
    ("let", let), ("in", in_), ("=", equal), (":=", dest_eq),
    ("if", if_), ("else", else_), ("elif", elif_),
    ("while", while_), ("for", for_),
    ("function", function),
    ("+", plus), ("-", minus), ("\\*", star), ("/", div), ("^", power), ("%", mod), ("\\*\\*", power2),
    ("==", eq), ("!=", neq), ("<=", leq), (">=", geq), ("<", lt), (">", gt),
    ("&", and_op), ("\\|", or_op), ("!", not_op), ("(true)|(false)", bool_term),
    ("@", amper), ("@@", double_amp),
    (f"({nonzero_digits})*|(({nonzero_digits})(0|{nonzero_digits})*.(0|{nonzero_digits})*)", number),
    (
        "\"(\x00|\x01|\x02|\x03|\x04|\x05|\x06|\x07|\x08|\t|\n|\x0b|\x0c|\r|\x0e|\x0f|\x10|\x11|\x12|\x13|\x14|\x15|\x16|\x17|\x18|\x19|\x1a|\x1b|\x1c|\x1d|\x1e|\x1f| |!|#|$|%|&|\'|\\(|\\)|\\*|+|,|-|.|/|0|1|2|3|4|5|6|7|8|9|:|;|<|=|>|?|@|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|[|\\\\|]|^|_|`|a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|{|\\||}|~|\x7f|\x80|\x81|\x82|\x83|\x84|\x85|\x86|\x87|\x88|\x89|\x8a|\x8b|\x8c|\x8d|\x8e|\x8f|\x90|\x91|\x92|\x93|\x94|\x95|\x96|\x97|\x98|\x99|\x9a|\x9b|\x9c|\x9d|\x9e|\x9f|\xa0|¡|¢|£|¤|¥|¦|§|¨|©|ª|«|¬|\xad|®|¯|°|±|²|³|´|µ|¶|·|¸|¹|º|»|¼|½|¾|¿|À|Á|Â|Ã|Ä|Å|Æ|Ç|È|É|Ê|Ë|Ì|Í|Î|Ï|Ð|Ñ|Ò|Ó|Ô|Õ|Ö|×|Ø|Ù|Ú|Û|Ü|Ý|Þ|ß|à|á|â|ã|ä|å|æ|ç|è|é|ê|ë|ì|í|î|ï|ð|ñ|ò|ó|ô|õ|ö|÷|ø|ù|ú|û|ü|ý|þ|ÿ)*\""
        , str_term),
    (
        "(#|$|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|_|a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|~|¡|¢|£|¤|¥|¦|§|¨|©|ª|«|¬|®|¯|°|±|²|³|µ|¶|·|¹|º|»|¼|½|¾|¿|À|Á|Â|Ã|Ä|Å|Æ|Ç|È|É|Ê|Ë|Ì|Í|Î|Ï|Ð|Ñ|Ò|Ó|Ô|Õ|Ö|×|Ø|Ù|Ú|Û|Ü|Ý|Þ|ß|à|á|â|ã|ä|å|æ|ç|è|é|ê|ë|ì|í|î|ï|ð|ñ|ò|ó|ô|õ|ö|÷|ø|ù|ú|û|ü|ý|þ|ÿ)(#|$|0|1|2|3|4|5|6|7|8|9|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|_|a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|~|¡|¢|£|¤|¥|¦|§|¨|©|ª|«|¬|®|¯|°|±|²|³|µ|¶|·|¹|º|»|¼|½|¾|¿|À|Á|Â|Ã|Ä|Å|Æ|Ç|È|É|Ê|Ë|Ì|Í|Î|Ï|Ð|Ñ|Ò|Ó|Ô|Õ|Ö|×|Ø|Ù|Ú|Û|Ü|Ý|Þ|ß|à|á|â|ã|ä|å|æ|ç|è|é|ê|ë|ì|í|î|ï|ð|ñ|ò|ó|ô|õ|ö|÷|ø|ù|ú|û|ü|ý|þ|ÿ)*"
        , idx),
    ("  *", Terminal("<spaces>", None))
]


class HulkLexer:
    def __init__(self) -> None:
        self.inicial = get_lexer(Regex_Terminal)

    def get_tokens(self, text: str):
        return [token for token in get_tokens(self.inicial, text) if token.token_type.Name != "<spaces>"]
