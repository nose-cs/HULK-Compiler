from src.Hulk_Grammar.hulk_grammar import obracket , cbracket, semicolon, opar, cpar, arrow, comma, colon, \
                                        let, _type, _in, equal, dest_eq,\
                                        _if, _else, _elif, \
                                        _while, _for, \
                                        function, \
                                        plus, minus, star, div, power, mod, power2, \
                                        eq, neq, leq, geq, gt, lt, \
                                        and_op, or_op, not_op, bool_term, \
                                        amper, double_amp, \
                                        str_term, number, _id

from src.lexer.lexer import get_lexer, get_tokens

Regex_Terminal = [
    ("[", obracket), ("]", cbracket), (";", semicolon), ("\\(", opar), ("\\)", cpar), ("=>", arrow), (",", comma),
    ("let", let), ("(class)|(def)", _type), ("in", _in), ("=", equal), (":=", dest_eq),
    ("if", _if), ("else", _else), ("elif", _elif),
    ("while", _while), ("for", _for),
    ("function", function),
    ("+", plus), ("-", minus), ("\\*", star), ("/", div), ("^", power), ("%", mod), ("**", power2),
    ("==", eq), ("!=", neq), ("<=", leq), (">=", geq), ("<", lt), (">", gt),
    ("&", and_op), ("\\|", or_op), ("!", not_op), ("(true)|(false)", bool_term),
    ("@", amper), ("@@", double_amp),
    ("\"(\x00|\x01|\x02|\x03|\x04|\x05|\x06|\x07|\x08|\t|\n|\x0b|\x0c|\r|\x0e|\x0f|\x10|\x11|\x12|\x13|\x14|\x15|\x16|\x17|\x18|\x19|\x1a|\x1b|\x1c|\x1d|\x1e|\x1f| |!|#|$|%|&|\'|\\(|\\)|\\*|+|,|-|.|/|0|1|2|3|4|5|6|7|8|9|:|;|<|=|>|?|@|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|[|\\\\|]|^|_|`|a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|{|\\||}|~|\x7f|\x80|\x81|\x82|\x83|\x84|\x85|\x86|\x87|\x88|\x89|\x8a|\x8b|\x8c|\x8d|\x8e|\x8f|\x90|\x91|\x92|\x93|\x94|\x95|\x96|\x97|\x98|\x99|\x9a|\x9b|\x9c|\x9d|\x9e|\x9f|\xa0|¡|¢|£|¤|¥|¦|§|¨|©|ª|«|¬|\xad|®|¯|°|±|²|³|´|µ|¶|·|¸|¹|º|»|¼|½|¾|¿|À|Á|Â|Ã|Ä|Å|Æ|Ç|È|É|Ê|Ë|Ì|Í|Î|Ï|Ð|Ñ|Ò|Ó|Ô|Õ|Ö|×|Ø|Ù|Ú|Û|Ü|Ý|Þ|ß|à|á|â|ã|ä|å|æ|ç|è|é|ê|ë|ì|í|î|ï|ð|ñ|ò|ó|ô|õ|ö|÷|ø|ù|ú|û|ü|ý|þ|ÿ)*\""
     , str_term),
    ("(1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*|((1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*.(0|1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*)"
     , number),
    ("(#|$|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|_|a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|~|¡|¢|£|¤|¥|¦|§|¨|©|ª|«|¬|®|¯|°|±|²|³|µ|¶|·|¹|º|»|¼|½|¾|¿|À|Á|Â|Ã|Ä|Å|Æ|Ç|È|É|Ê|Ë|Ì|Í|Î|Ï|Ð|Ñ|Ò|Ó|Ô|Õ|Ö|×|Ø|Ù|Ú|Û|Ü|Ý|Þ|ß|à|á|â|ã|ä|å|æ|ç|è|é|ê|ë|ì|í|î|ï|ð|ñ|ò|ó|ô|õ|ö|÷|ø|ù|ú|û|ü|ý|þ|ÿ)(#|$|0|1|2|3|4|5|6|7|8|9|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|_|a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|~|¡|¢|£|¤|¥|¦|§|¨|©|ª|«|¬|®|¯|°|±|²|³|µ|¶|·|¹|º|»|¼|½|¾|¿|À|Á|Â|Ã|Ä|Å|Æ|Ç|È|É|Ê|Ë|Ì|Í|Î|Ï|Ð|Ñ|Ò|Ó|Ô|Õ|Ö|×|Ø|Ù|Ú|Û|Ü|Ý|Þ|ß|à|á|â|ã|ä|å|æ|ç|è|é|ê|ë|ì|í|î|ï|ð|ñ|ò|ó|ô|õ|ö|÷|ø|ù|ú|û|ü|ý|þ|ÿ)*"
     , _id)
]

class Hulk_Lexer:
    def __init__(self) -> None:
        self.inicial = get_lexer(Regex_Terminal)

    def get_tokens(self, text: str):
        return get_tokens(self.inicial, text)