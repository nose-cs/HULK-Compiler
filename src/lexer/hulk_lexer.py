from cmp.Hulk_Grammar.hulk_grammar import obracket , cbracket, semicolon, opar, cpar, arrow, comma, \
                                        let, _type, _in, equal, \
                                        _if, _else, _elif, \
                                        _while, _for, \
                                        plus, minus, star, div, power, \
                                        and_op, or_op, not_op, bool_term, \
                                        number, _id

from src.lexer.lexer import get_lexer, get_tokens

Regex_Terminal = [
    ("[", obracket), ("]", cbracket), (";", semicolon), ("\\(", opar), ("\\)", cpar), ("=>", arrow), (",", comma),
    ("let", let), ("(class)|(def)", _type), ("in", _in), ("=", equal),
    ("if", _if), ("else", _else), ("elif", _elif),
    ("while", _while), ("for", _for),
    ("+", plus), ("-", minus), ("\\*", star), ("/", div), ("^", power),
    ("&", and_op), ("\\|", or_op), ("!", not_op), ("(true)|(false)", bool_term),
    ("(1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*|((1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*.(0|1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*)", number),
    ("(#|$|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|_|a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|~|¡|¢|£|¤|¥|¦|§|¨|©|ª|«|¬|®|¯|°|±|²|³|µ|¶|·|¹|º|»|¼|½|¾|¿|À|Á|Â|Ã|Ä|Å|Æ|Ç|È|É|Ê|Ë|Ì|Í|Î|Ï|Ð|Ñ|Ò|Ó|Ô|Õ|Ö|×|Ø|Ù|Ú|Û|Ü|Ý|Þ|ß|à|á|â|ã|ä|å|æ|ç|è|é|ê|ë|ì|í|î|ï|ð|ñ|ò|ó|ô|õ|ö|÷|ø|ù|ú|û|ü|ý|þ|ÿ)(#|$|0|1|2|3|4|5|6|7|8|9|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|_|a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|~|¡|¢|£|¤|¥|¦|§|¨|©|ª|«|¬|®|¯|°|±|²|³|µ|¶|·|¹|º|»|¼|½|¾|¿|À|Á|Â|Ã|Ä|Å|Æ|Ç|È|É|Ê|Ë|Ì|Í|Î|Ï|Ð|Ñ|Ò|Ó|Ô|Õ|Ö|×|Ø|Ù|Ú|Û|Ü|Ý|Þ|ß|à|á|â|ã|ä|å|æ|ç|è|é|ê|ë|ì|í|î|ï|ð|ñ|ò|ó|ô|õ|ö|÷|ø|ù|ú|û|ü|ý|þ|ÿ)*"
     , _id)
]

class Hulk_Lexer:
    def __init__(self) -> None:
        self.inicial = get_lexer(Regex_Terminal)

    def get_tokens(self, text: str):
        return get_tokens(self.inicial, text)