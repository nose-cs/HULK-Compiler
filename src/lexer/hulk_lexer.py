import sys

import dill

import src.hulk_grammar.hulk_grammar as hulk_grammar
from src.errors import HulkLexicographicError
from src.lexer.hulk_token_types import TokenType
from src.lexer.lexer import Lexer

operators = [
    ("{", TokenType.OPEN_BRACKET), ("}", TokenType.CLOSE_BRACKET), (";", TokenType.SEMICOLON),
    ("\\(", TokenType.OPEN_PAREN), ("\\)", TokenType.CLOSE_PAREN), ("=>", TokenType.ARROW), (",", TokenType.COMMA),
    ("=", TokenType.ASSIGMENT), (":=", TokenType.DEST_ASSIGMENT),
    ("+", TokenType.PLUS), ("-", TokenType.MINUS), ("\\*", TokenType.STAR), ("/", TokenType.DIV),
    ("^", TokenType.POWER), ("%", TokenType.MOD), ("\\*\\*", TokenType.POWER2),
    ("==", TokenType.EQ), ("!=", TokenType.NEQ), ("<=", TokenType.LEQ), (">=", TokenType.GEQ),
    ("<", TokenType.LT), (">", TokenType.GT), ("&", TokenType.AND), ("\\|", TokenType.OR),
    ("!", TokenType.NOT), ("@", TokenType.AMP), ("@@", TokenType.DOUBLE_AMP), (".", TokenType.DOT),
    (":", TokenType.COLON), ("\\|\\|", TokenType.DOUBLE_BAR), ("\\[", TokenType.OPEN_SQUARE_BRACKET),
    ("\\]", TokenType.CLOSE_SQUARE_BRACKET)]

reserved_words = [("let", TokenType.LET), ("in", TokenType.IN),
                  ("if", TokenType.IF), ("else", TokenType.ELSE), ("elif", TokenType.ELIF),
                  ("function", TokenType.FUNCTION),
                  ("while", TokenType.WHILE), ("for", TokenType.FOR),
                  ("new", TokenType.NEW), ("is", TokenType.IS), ("as", TokenType.AS),
                  ("protocol", TokenType.PROTOCOL), ("extends", TokenType.EXTENDS),
                  ("type", TokenType.TYPE), ("inherits", TokenType.INHERITS), ("base", TokenType.BASE),
                  ("true|false", TokenType.BOOLEAN)]

nonzero_digits = '|'.join(str(n) for n in range(1, 10))
digits = '|'.join(str(n) for n in range(10))
lower_letters = '|'.join(chr(n) for n in range(ord('a'), ord('z') + 1))
upper_letters = '|'.join(chr(n) for n in range(ord('A'), ord('Z') + 1))

string_regex = "\"(\\\\\"|\\x00|\\x01|\\x02|\\x03|\\x04|\\x05|\\x06|\\x07|\\x08|\\t|\\n|\\x0b|\\x0c|\\r|\\x0e|\\x0f|\\x10|\\x11|\\x12|\\x13|\\x14|\\x15|\\x16|\\x17|\\x18|\\x19|\\x1a|\\x1b|\\x1c|\\x1d|\\x1e|\\x1f| |!|#|$|%|&|\'|\\(|\\)|\\*|+|,|-|.|/|0|1|2|3|4|5|6|7|8|9|:|;|<|=|>|?|@|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|[|\\\\|]|^|_|`|a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|{|\\||}|~|\\x7f|\\x80|\\x81|\\x82|\\x83|\\x84|\\x85|\\x86|\\x87|\\x88|\\x89|\\x8a|\\x8b|\\x8c|\\x8d|\\x8e|\\x8f|\\x90|\\x91|\\x92|\\x93|\\x94|\\x95|\\x96|\\x97|\\x98|\\x99|\\x9a|\\x9b|\\x9c|\\x9d|\\x9e|\\x9f|\\xa0|¡|¢|£|¤|¥|¦|§|¨|©|ª|«|¬|\\xad|®|¯|°|±|²|³|´|µ|¶|·|¸|¹|º|»|¼|½|¾|¿|À|Á|Â|Ã|Ä|Å|Æ|Ç|È|É|Ê|Ë|Ì|Í|Î|Ï|Ð|Ñ|Ò|Ó|Ô|Õ|Ö|×|Ø|Ù|Ú|Û|Ü|Ý|Þ|ß|à|á|â|ã|ä|å|æ|ç|è|é|ê|ë|ì|í|î|ï|ð|ñ|ò|ó|ô|õ|ö|÷|ø|ù|ú|û|ü|ý|þ|ÿ)*\""

unterminated_string_regex = "\"(\\x00|\\x01|\\x02|\\x03|\\x04|\\x05|\\x06|\\x07|\\x08|\\t|\\n|\\x0b|\\x0c|\\r|\\x0e|\\x0f|\\x10|\\x11|\\x12|\\x13|\\x14|\\x15|\\x16|\\x17|\\x18|\\x19|\\x1a|\\x1b|\\x1c|\\x1d|\\x1e|\\x1f| |!|#|$|%|&|\'|\\(|\\)|\\*|+|,|-|.|/|0|1|2|3|4|5|6|7|8|9|:|;|<|=|>|?|@|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|[|\\\\|]|^|_|`|a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|{|\\||}|~|\\x7f|\\x80|\\x81|\\x82|\\x83|\\x84|\\x85|\\x86|\\x87|\\x88|\\x89|\\x8a|\\x8b|\\x8c|\\x8d|\\x8e|\\x8f|\\x90|\\x91|\\x92|\\x93|\\x94|\\x95|\\x96|\\x97|\\x98|\\x99|\\x9a|\\x9b|\\x9c|\\x9d|\\x9e|\\x9f|\\xa0|¡|¢|£|¤|¥|¦|§|¨|©|ª|«|¬|\\xad|®|¯|°|±|²|³|´|µ|¶|·|¸|¹|º|»|¼|½|¾|¿|À|Á|Â|Ã|Ä|Å|Æ|Ç|È|É|Ê|Ë|Ì|Í|Î|Ï|Ð|Ñ|Ò|Ó|Ô|Õ|Ö|×|Ø|Ù|Ú|Û|Ü|Ý|Þ|ß|à|á|â|ã|ä|å|æ|ç|è|é|ê|ë|ì|í|î|ï|ð|ñ|ò|ó|ô|õ|ö|÷|ø|ù|ú|û|ü|ý|þ|ÿ)*"

number_regex = '|'.join([f"({nonzero_digits})({digits})*",
                         f"({nonzero_digits})({digits})*.({digits})({digits})*",
                         f"0.({digits})({digits})*",
                         "0"])

identifier_regex = f"(_|{upper_letters}|{lower_letters})(_|{upper_letters}|{lower_letters}|{digits})*"

hulk_tokens = operators + reserved_words + [
    (number_regex, TokenType.NUMBER), (identifier_regex, TokenType.IDENTIFIER),
    (string_regex, TokenType.STRING), (unterminated_string_regex, TokenType.UNTERMINATED_STRING),
    ("  *", TokenType.SPACES), ("\n|\t", TokenType.ESCAPED_CHAR)
]

# Tokens that are going to be used to synchronize the lexer when an error occurs
hulk_lexer_synchronizing_tokens = [("  *", TokenType.SPACES), ("\n|\t", TokenType.ESCAPED_CHAR)] + operators


class HulkLexer(Lexer):
    def __init__(self, rebuild=False, convert_to_dfa=False, save=False) -> None:
        super().__init__(hulk_tokens, hulk_grammar.G.EOF, rebuild, convert_to_dfa, hulk_lexer_synchronizing_tokens)

        if not rebuild:
            try:
                with open('src/lexer/hulk_lexer.pkl', 'rb') as automaton_pkl:
                    self.automaton = dill.load(automaton_pkl)
                with open('src/lexer/hulk_lexer_synchronizing.pkl', 'rb') as synchronizing_automaton_pkl:
                    self.synchronizing_automaton = dill.load(synchronizing_automaton_pkl)
            except:
                super().__init__(hulk_tokens, hulk_grammar.G.EOF, True, convert_to_dfa, hulk_lexer_synchronizing_tokens)

        if save:
            sys.setrecursionlimit(10000)

            with open('src/lexer/hulk_lexer.pkl', 'wb') as automaton_pkl:
                dill.dump(self.automaton, automaton_pkl)
            with open('src/lexer/hulk_lexer_synchronizing.pkl', 'wb') as synchronizing_automaton_pkl:
                dill.dump(self.synchronizing_automaton, synchronizing_automaton_pkl)

    @staticmethod
    def report_errors(tokens):
        errors = []
        for token in tokens:
            if not token.is_valid:
                error_text = HulkLexicographicError.UNKNOWN_TOKEN % token.lex
                errors.append(HulkLexicographicError(error_text, token.row, token.column))
            elif token.token_type == TokenType.UNTERMINATED_STRING:
                error_text = HulkLexicographicError.UNTERMINATED_STRING % token.lex
                errors.append(HulkLexicographicError(error_text, token.row, token.column))
        return errors

    def __call__(self, text):
        tokens = super().__call__(text)
        errors = self.report_errors(tokens)
        filtered_tokens = [token for token in tokens if token.is_valid and
                           token.token_type not in [TokenType.SPACES, TokenType.ESCAPED_CHAR,
                                                    TokenType.UNTERMINATED_STRING]]
        return filtered_tokens, errors
