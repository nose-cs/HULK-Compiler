class HulkError(Exception):
    def __init__(self, text):
        super().__init__(text)

    @property
    def error_type(self):
        return 'HulkError'

    @property
    def text(self):
        return self.args[0]

    def __str__(self):
        return f'{self.error_type}: {self.text}'

    def __repr__(self):
        return str(self)


class IOHulkError(HulkError):
    def __init__(self, text, path):
        super().__init__(text)
        self.path = path

    INVALID_EXTENSION = 'Input file %s is not a .hulk file.'
    ERROR_READING_FILE = 'Error reading file %s.'
    ERROR_WRITING_FILE = 'Error writing to file %s.'

    def __str__(self):
        return f'{self.error_type}: {self.text}' % self.path

    @property
    def error_type(self):
        return 'IOHulkError'


class LexicographicError(HulkError):
    def __init__(self, text, line, column):
        super().__init__(text)
        self.line = line
        self.column = column

    def __str__(self):
        return f'({self.line}, {self.column}) - {self.error_type}: {self.text}'

    UNKNOWN_TOKEN = 'Unknown token'
    UNTERMINATED_STRING = 'Unterminated string constant'

    @property
    def error_type(self):
        return 'LexicographicError'


class SyntacticError(HulkError):
    ERROR = 'Error at or near "%s"'

    @property
    def error_type(self):
        return 'SyntacticError'


class SemanticError(HulkError):
    WRONG_SIGNATURE = 'Method "%s" already defined in "%s" with a different signature.'
    SELF_IS_READONLY = 'Variable "self" is read-only.'
    LOCAL_ALREADY_DEFINED = 'Variable "%s" is already defined in method "%s".'
    INCOMPATIBLE_TYPES = 'Cannot convert "%s" into "%s".'
    VARIABLE_NOT_DEFINED = 'Variable "%s" is not defined in "%s".'
    INVALID_OPERATION = 'Operation is not defined between "%s" and "%s".'
    INCONSISTENT_USE = 'Inconsistent use of "%s".'

    @property
    def error_type(self):
        return 'SemanticError'
