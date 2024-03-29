import itertools as itt

from src.errors import SemanticError
from src.semantics.types import Type, Protocol, AutoType


class Function:
    def __init__(self, name, param_names, param_types, return_type, node=None):
        self.name = name
        self.node = node
        self.param_names = param_names
        self.param_types = param_types
        self.return_type = return_type

    def __str__(self):
        params = ', '.join(f'{n}:{t.name}' for n, t in zip(self.param_names, self.param_types))
        return '\n' + f'function {self.name}({params}): {self.return_type.name};' + '\n'

    def __eq__(self, other):
        return other.name == self.name and \
            other.return_type == self.return_type and \
            other.param_types == self.param_types


class Context:
    def __init__(self):
        self.types = {}
        self.protocols = {}
        self.functions = {}

    def create_type(self, name: str, node=None) -> Type:
        if name in self.types:
            raise SemanticError(f'Type with the same name ({name}) already in context.')
        if name in self.protocols:
            raise SemanticError(f'Protocol with the same name ({name}) already in context.')
        typex = self.types[name] = Type(name, node)
        return typex

    def get_type(self, name: str) -> Type:
        try:
            return self.types[name]
        except KeyError:
            raise SemanticError(f'Type "{name}" is not defined.')

    def create_protocol(self, name: str, node=None) -> Protocol:
        if name in self.protocols:
            raise SemanticError(f'Protocol with the same name ({name}) already in context.')
        if name in self.types:
            raise SemanticError(f'Type with the same name ({name}) already in context.')
        protocol = self.protocols[name] = Protocol(name, node)
        return protocol

    def get_protocol(self, name: str) -> Protocol:
        try:
            return self.protocols[name]
        except KeyError:
            raise SemanticError(f'Protocol "{name}" is not defined.')

    def get_type_or_protocol(self, name: str) -> tuple[Type, Protocol]:
        try:
            return self.get_protocol(name)
        except SemanticError:
            return self.get_type(name)

    def create_function(self, name: str, params_names: list, params_types: list, return_type, node=None) -> Function:
        if name in self.functions:
            raise SemanticError(f'Function with the same name ({name}) already in context.')
        function = self.functions[name] = Function(name, params_names, params_types, return_type, node)
        return function

    def get_function(self, name: str) -> Function:
        try:
            return self.functions[name]
        except KeyError:
            raise SemanticError(f'Function "{name}" is not defined.')

    def __str__(self):
        return ('{\n\t' +
                '\n\t'.join(y for x in self.types.values() for y in str(x).split('\n')) +
                '\n\t'.join(y for x in self.protocols.values() for y in str(x).split('\n')) +
                '\n\t'.join(y for x in self.functions.values() for y in str(x).split('\n')) +
                '\n}')

    def __repr__(self):
        return str(self)


class VariableInfo:
    def __init__(self, name, vtype):
        self.name = name
        self.type = vtype
        self.nameC = None

    def setNameC(self, name: str):
        self.nameC = name

    def __str__(self):
        return f'{self.name} : {self.type.name}'

    def __repr__(self):
        return str(self)


class Scope:
    def __init__(self, parent=None):
        self.locals = []
        self.parent: Scope = parent
        self.children = []
        self.index = 0 if parent is None else len(parent)

    def __len__(self):
        return len(self.locals)

    def create_child(self):
        child = Scope(self)
        self.children.append(child)
        return child

    def define_variable(self, var_name, var_type) -> VariableInfo:
        info = VariableInfo(var_name, var_type)
        self.locals.append(info)
        return info

    def find_variable(self, var_name: str, index=None) -> VariableInfo:
        local_vars = self.locals if index is None else itt.islice(self.locals, index)
        try:
            return next(x for x in local_vars if x.name == var_name)
        except StopIteration:
            return self.parent.find_variable(var_name, self.index) if self.parent is not None else None

    def is_defined(self, var_name: str) -> bool:
        return self.find_variable(var_name) is not None

    def is_local(self, var_name: str) -> bool:
        return any(True for x in self.locals if x.name == var_name)

    def __str__(self):
        return self.tab_level(1, '', 1)

    def tab_level(self, tabs, name, num) -> str:
        res = ('\t' * tabs) + ('\n' + ('\t' * tabs)).join(str(local) for local in self.locals)
        children = '\n'.join(child.tab_level(tabs + 1, num, num + 1) for child in self.children)
        return "\t" * (tabs - 1) + f'{name}' + "\t" * tabs + f'\n{res}\n{children}'

    def __repr__(self):
        return str(self)

    def there_is_auto_type_in_scope(self) -> bool:
        return any(True for x in self.locals if x.type == AutoType()) or \
            any(True for child in self.children if child.there_is_auto_type_in_scope())
