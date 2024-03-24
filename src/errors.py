class HulkError(Exception):
    def __init__(self, text, line, column):
        super().__init__(text)
        self.line = line
        self.column = column

    @property
    def error_type(self):
        return 'HulkError'

    @property
    def text(self):
        return self.args[0]

    def __str__(self):
        return f'({self.line}, {self.column}) - {self.error_type}: {self.text}'

    def __repr__(self):
        return str(self)


class LexicographicError(HulkError):
    UNKNOWN_TOKEN = 'Unknown token'
    UNTERMINATED_STRING = 'Unterminated string constant'
    EOF_STRING = 'EOF in string constant'

    @property
    def error_type(self):
        return 'LexicographicError'


class SyntacticError(HulkError):
    ERROR = 'ERROR at or near "%s"'

    @property
    def error_type(self):
        return 'SyntacticError'
