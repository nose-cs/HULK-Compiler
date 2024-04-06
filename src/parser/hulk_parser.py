from typing import List

import src.hulk_grammar.hulk_grammar as hulk_grammar
from src.errors import HulkSyntacticError
from src.lexer.hulk_token_types import TokenType
from src.parsing import LR1Parser, ParserError
from src.utils import Token


class HulkParser(LR1Parser):
    def __init__(self):
        super().__init__(hulk_grammar.G)

    def __call__(self, tokens: List[Token]):
        try:
            mapped_terminals = [tokens_terminals_map[t.token_type] for t in tokens]
            derivation, operations = super().__call__(mapped_terminals)
            return derivation, operations, []
        except ParserError as e:
            error_token = tokens[e.token_index]
            error_text = HulkSyntacticError.PARSING_ERROR % error_token.lex
            errors = [HulkSyntacticError(error_text, error_token.row, error_token.column)]
            return None, None, errors


tokens_terminals_map = {
    hulk_grammar.G.EOF: hulk_grammar.G.EOF,
    TokenType.OPEN_PAREN: hulk_grammar.opar,
    TokenType.CLOSE_PAREN: hulk_grammar.cpar,
    TokenType.OPEN_BRACKET: hulk_grammar.obracket,
    TokenType.CLOSE_BRACKET: hulk_grammar.cbracket,
    TokenType.OPEN_SQUARE_BRACKET: hulk_grammar.o_square_bracket,
    TokenType.CLOSE_SQUARE_BRACKET: hulk_grammar.c_square_bracket,
    TokenType.COMMA: hulk_grammar.comma,
    TokenType.DOT: hulk_grammar.dot,
    TokenType.COLON: hulk_grammar.colon,
    TokenType.SEMICOLON: hulk_grammar.semicolon,
    TokenType.ARROW: hulk_grammar.arrow,
    TokenType.DOUBLE_BAR: hulk_grammar.double_bar,
    TokenType.ASSIGMENT: hulk_grammar.equal,
    TokenType.DEST_ASSIGMENT: hulk_grammar.dest_eq,

    TokenType.IDENTIFIER: hulk_grammar.idx,
    TokenType.STRING: hulk_grammar.string_literal,
    TokenType.NUMBER: hulk_grammar.number_literal,
    TokenType.BOOLEAN: hulk_grammar.bool_literal,

    # Arithmetic operators
    TokenType.PLUS: hulk_grammar.plus,
    TokenType.MINUS: hulk_grammar.minus,
    TokenType.STAR: hulk_grammar.star,
    TokenType.DIV: hulk_grammar.div,
    TokenType.MOD: hulk_grammar.mod,
    TokenType.POWER: hulk_grammar.power,
    TokenType.POWER2: hulk_grammar.power2,

    # Boolean operators
    TokenType.AND: hulk_grammar.and_op,
    TokenType.OR: hulk_grammar.or_op,
    TokenType.NOT: hulk_grammar.not_op,

    # Concat strings operators
    TokenType.AMP: hulk_grammar.amper,
    TokenType.DOUBLE_AMP: hulk_grammar.double_amp,

    # Comparison operators
    TokenType.EQ: hulk_grammar.eq,
    TokenType.NEQ: hulk_grammar.neq,
    TokenType.LEQ: hulk_grammar.leq,
    TokenType.GEQ: hulk_grammar.geq,
    TokenType.LT: hulk_grammar.lt,
    TokenType.GT: hulk_grammar.gt,

    # Keywords
    TokenType.FUNCTION: hulk_grammar.function,
    TokenType.LET: hulk_grammar.let,
    TokenType.IN: hulk_grammar.in_,
    TokenType.IF: hulk_grammar.if_,
    TokenType.ELSE: hulk_grammar.else_,
    TokenType.ELIF: hulk_grammar.elif_,
    TokenType.WHILE: hulk_grammar.while_,
    TokenType.FOR: hulk_grammar.for_,
    TokenType.NEW: hulk_grammar.new,
    TokenType.IS: hulk_grammar.is_,
    TokenType.AS: hulk_grammar.as_,
    TokenType.PROTOCOL: hulk_grammar.protocol,
    TokenType.EXTENDS: hulk_grammar.extends,
    TokenType.TYPE: hulk_grammar.word_type,
    TokenType.INHERITS: hulk_grammar.inherits,
    TokenType.BASE: hulk_grammar.base,
}
