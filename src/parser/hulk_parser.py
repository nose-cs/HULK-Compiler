from typing import List

from src.errors import SyntacticError
from src.hulk_grammar.hulk_grammar import G
from src.parsing import LR1Parser, ParserError
from src.utils import Token


class HulkParser(LR1Parser):
    def __init__(self):
        super().__init__(G)
        self.errors = []

    def __call__(self, tokens: List[Token]):
        try:
            derivation, operations = super().__call__([t.token_type for t in tokens])
            return derivation, operations, []
        except ParserError as e:
            error_token = tokens[e.token_index]
            error_text = SyntacticError.ERROR % error_token.lex
            errors = [SyntacticError(error_text, error_token.row, error_token.column)]
            return None, None, errors
