from collections import OrderedDict

from src.errors import SemanticError


class Attribute:
    def __init__(self, name, typex):
        self.name = name
        self.type = typex

    def __str__(self):
        return f'[attrib] {self.name} : {self.type.name};'

    def __repr__(self):
        return str(self)


class Method:
    def __init__(self, name, param_names, params_types, return_type, node=None):
        self.name = name
        self.node = node
        self.param_names = param_names
        self.param_types = params_types
        self.return_type = return_type

    def __str__(self):
        params = ', '.join(f'{n}:{t.name}' for n, t in zip(self.param_names, self.param_types))
        return f'[method] {self.name}({params}): {self.return_type.name};'

    def __eq__(self, other):
        return other.name == self.name and \
            other.return_type == self.return_type and \
            other.param_types == self.param_types

    def can_substitute_with(self, other):
        if self.name != other.name:
            return False
        if not other.return_type.conforms_to(self.return_type):
            return False
        if len(self.param_types) != len(other.param_types):
            return False
        for meth_type, impl_type in zip(self.param_types, other.param_types):
            if not meth_type.conforms_to(impl_type):
                return False
        return True


class Protocol:
    def __init__(self, name: str, node=None):
        self.name = name
        self.node = node
        self.methods = []
        self.parent = None

    def set_parent(self, parent):
        if self.parent is not None:
            raise SemanticError(f'Parent type is already set for {self.name}.')
        self.parent = parent

    def get_method(self, name: str):
        try:
            return next(method for method in self.methods if method.name == name)
        except StopIteration:
            if self.parent is None:
                raise SemanticError(f'Method "{name}" is not defined in {self.name}.')
            try:
                return self.parent.get_method(name)
            except SemanticError:
                raise SemanticError(f'Method "{name}" is not defined in {self.name}.')

    def define_method(self, name: str, param_names: list, param_types: list, return_type, node=None):
        if name in (method.name for method in self.methods):
            raise SemanticError(f'Method "{name}" already defined in {self.name}')
        method = Method(name, param_names, param_types, return_type, node)
        self.methods.append(method)
        return method

    def _not_ancestor_conforms_to(self, other):
        if not isinstance(other, Protocol):
            return False
        try:
            return all(method.can_substitute_with(self.get_method(method.name)) for method in other.methods)
        # If a method is not defined in the current type (or its ancestors), then it is not conforming
        except SemanticError:
            return False

    def conforms_to(self, other):
        if isinstance(other, Type):
            return False
        return self == other or self.parent is not None and self.parent.conforms_to(
            other) or self._not_ancestor_conforms_to(other)

    def __str__(self):
        output = f'protocol {self.name}'
        parent = '' if self.parent is None else f' extends {self.parent.name}'
        output += parent
        output += ' {'
        output += '\n\t' if self.methods else ''
        output += '\n\t'.join(str(x) for x in self.methods)
        output += '\n' if self.methods else ''
        output += '}\n'
        return output

    def __repr__(self):
        return str(self)


class Type:
    def __init__(self, name: str, node=None):
        self.name = name
        self.node = node
        self.params_names = []
        self.params_types = []
        self.attributes = []
        self.attributes_types = []
        self.methods = []
        self.parent = None

    def set_parent(self, parent):
        if self.parent is not None:
            raise SemanticError(f'Parent type is already set for {self.name}.')
        self.parent = parent

    def get_attribute(self, name: str) -> Attribute:
        try:
            return next(attr for attr in self.attributes if attr.name == name)
        except StopIteration:
            raise SemanticError(f'Attribute "{name}" is not defined in {self.name}.')

    def define_attribute(self, name: str, typex) -> Attribute:
        try:
            self.get_attribute(name)
        except SemanticError:
            attribute = Attribute(name, typex)
            self.attributes.append(attribute)
            return attribute
        else:
            raise SemanticError(f'Attribute "{name}" is already defined in {self.name}.')

    def get_method(self, name: str) -> Method:
        try:
            return next(method for method in self.methods if method.name == name)
        except StopIteration:
            if self.parent is None:
                raise SemanticError(f'Method "{name}" is not defined in {self.name}.')
            try:
                return self.parent.get_method(name)
            except SemanticError:
                raise SemanticError(f'Method "{name}" is not defined in {self.name}.')

    def define_method(self, name: str, param_names: list, param_types: list, return_type, node=None) -> Method:
        if name in (method.name for method in self.methods):
            raise SemanticError(f'Method "{name}" already defined in {self.name}')
        method = Method(name, param_names, param_types, return_type, node)
        self.methods.append(method)
        return method

    def set_params(self, params_names, params_types) -> None:
        self.params_names = params_names
        self.params_types = params_types

    def all_attributes(self, clean=True):
        plain = OrderedDict() if self.parent is None else self.parent.all_attributes(False)
        for attr in self.attributes:
            plain[attr.name] = (attr, self)
        return plain.values() if clean else plain

    def all_methods(self, clean=True):
        plain = OrderedDict() if self.parent is None else self.parent.all_methods(False)
        for method in self.methods:
            plain[method.name] = (method, self)
        return plain.values() if clean else plain

    def conforms_to(self, other):
        if isinstance(other, Type):
            return other.bypass() or self == other or self.parent is not None and self.parent.conforms_to(other)
        elif isinstance(other, Protocol):
            try:
                return all(method.can_substitute_with(self.get_method(method.name)) for method in other.methods)
            # If a method is not defined in the current type (or its ancestors), then it is not conforming
            except SemanticError:
                return False

    def bypass(self):
        return False

    def __str__(self):
        output = f'type {self.name}'
        parent = '' if self.parent is None else f' inherits {self.parent.name}'
        output += parent
        output += ' {'
        output += '\n\t' if self.attributes or self.methods else ''
        output += '\n\t'.join(str(x) for x in self.attributes)
        output += '\n\t' if self.attributes else ''
        output += '\n\t'.join(str(x) for x in self.methods)
        output += '\n' if self.methods else ''
        output += '}\n'
        return output

    def __repr__(self):
        return str(self)


class ErrorType(Type):
    def __init__(self):
        Type.__init__(self, '<error>')

    def conforms_to(self, other):
        return True

    def bypass(self):
        return True

    def __eq__(self, other):
        return isinstance(other, Type)


class AutoType(Type):
    def __init__(self):
        Type.__init__(self, '<auto>')

    def __eq__(self, other):
        return isinstance(other, AutoType) or other.name == self.name


class StringType(Type):
    def __init__(self):
        super().__init__('String')

    def __eq__(self, other):
        return isinstance(other, StringType) or other.name == self.name


class BoolType(Type):
    def __init__(self):
        super().__init__('Bool')

    def __eq__(self, other):
        return isinstance(other, BoolType) or other.name == self.name


class NumberType(Type):
    def __init__(self) -> None:
        super().__init__('Number')

    def __eq__(self, other):
        return isinstance(other, NumberType) or other.name == self.name


class ObjectType(Type):
    def __init__(self) -> None:
        super().__init__('Object')

    def __eq__(self, other):
        return isinstance(other, ObjectType) or other.name == self.name


class SelfType(Type):
    def __init__(self) -> None:
        super().__init__('Self')


def get_most_specialized_type(types):
    if not types or any(isinstance(t, ErrorType) for t in types):
        return ErrorType()
    most_specialized = types[0]
    for typex in types[1:]:
        if typex.conforms_to(most_specialized):
            most_specialized = typex
        elif not most_specialized.conforms_to(typex):
            return ErrorType()
    return most_specialized


def get_lowest_common_ancestor(types):
    if not types or any(isinstance(t, ErrorType) for t in types):
        return ErrorType()
    lca = types[0]
    for typex in types[1:]:
        lca = _get_lca(lca, typex)
    return lca


def _get_lca(type1, type2):
    if type1.conforms_to(type2):
        return type2
    if type2.conforms_to(type1):
        return type1
    return _get_lca(type1.parent, type2.parent)
