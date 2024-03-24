class Type:
    def __init__(self, id) -> None:
        self.id = id
        self.args_names = []
        self.args_types = []
        self.propierties_ids = []
        self.propierties_types = []
        self.methods = {}


class StringType(Type):
    def __init__(self) -> None:
        super().__init__('String')

class BoolType(Type):
    def __init__(self) -> None:
        super().__init__('Bool')

class NumberType(Type):
    def __init__(self) -> None:
        super().__init__('Number')

class ObjectType(Type):
    def __init__(self, id) -> None:
        super().__init__('Object')        