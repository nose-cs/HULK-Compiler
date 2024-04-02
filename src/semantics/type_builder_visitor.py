import src.hulk_grammar.hulk_ast_nodes as hulk_nodes
import src.visitor as visitor
from src.errors import SemanticError
from src.semantics.types import ErrorType, AutoType
from src.semantics.utils import Context


class TypeBuilder(object):
    def __init__(self, context, errors=None) -> None:
        if errors is None:
            errors = []
        self.context: Context = context
        self.current_type = None
        self.errors: list = errors

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(hulk_nodes.ProgramNode)
    def visit(self, node: hulk_nodes.ProgramNode):
        for declaration in node.declarations:
            self.visit(declaration)

    @visitor.when(hulk_nodes.FunctionDeclarationNode)
    def visit(self, node: hulk_nodes.FunctionDeclarationNode):
        params_names, params_types = self.get_params_names_and_types(node)

        if node.return_type is None:
            return_type = AutoType()
        else:
            try:
                # Check if the return type is declared
                return_type = self.context.get_type_or_protocol(node.return_type)
            except SemanticError as e:
                self.errors.append(e)
                return_type = ErrorType()

        try:
            return self.context.create_function(node.id, params_names, params_types, return_type, node)
        except SemanticError as e:
            self.errors.append(e)

    def get_params_names_and_types(self, node):
        # for types that not specify params
        if node.params_ids is None or node.params_types is None:
            return None, None

        params_names = []
        params_types = []

        # Check that params are not repeated
        if len(node.params_ids) != len(set(node.params_ids)):
            self.errors.append(SemanticError('Cannot have two parameters with the same name in %s'))

        for i in range(len(node.params_ids)):
            # If the param is already declared, skip it
            if node.params_ids[i] in params_names:
                continue
            try:
                if node.params_types[i] is None:
                    param_type = AutoType()
                    params_types.append(param_type)
                else:
                    # Check if the param type is declared
                    param_type = self.context.get_type_or_protocol(node.params_types[i])
                    params_types.append(param_type)
            except SemanticError as e:
                self.errors.append(e)
                params_types.append(ErrorType())
            params_names.append(node.params_ids[i])

        return params_names, params_types

    @visitor.when(hulk_nodes.TypeDeclarationNode)
    def visit(self, node: hulk_nodes.TypeDeclarationNode):
        self.current_type = self.context.get_type(node.idx)

        self.current_type.params_names, self.current_type.params_types = self.get_params_names_and_types(node)

        # Check if the type is inheriting from a forbidden type
        if node.parent in ['Number', 'Boolean', 'String', 'Self']:
            self.errors.append(SemanticError(f'Type {node.idx} is inheriting from a forbidden type  -_-'))
        elif node.parent is not None:
            try:
                # Look for a circular dependency
                parent = self.context.get_type(node.parent)
                current = parent
                while current is not None:
                    if current.name == self.current_type.name:
                        self.errors.append(SemanticError('Circular dependency inheritance  :O'))
                        parent = ErrorType()
                        break
                    current = current.parent
            except SemanticError as e:
                # If the parent type is not declared, set it to ErrorType
                self.errors.append(e)
                parent = ErrorType()
            try:
                self.current_type.set_parent(parent)
            except SemanticError as e:
                # If the parent type is already set
                self.errors.append(e)
        else:
            object_type = self.context.get_type('Object')
            self.current_type.set_parent(object_type)

        for attribute in node.attributes:
            self.visit(attribute)

        for method in node.methods:
            self.visit(method)

    @visitor.when(hulk_nodes.MethodDeclarationNode)
    def visit(self, node: hulk_nodes.MethodDeclarationNode):
        params_names, params_types = self.get_params_names_and_types(node)

        if node.return_type is None:
            return_type = AutoType()
        else:
            try:
                # Check if the return type is declared
                return_type = self.context.get_type_or_protocol(node.return_type)
            except SemanticError as e:
                self.errors.append(e)
                return_type = ErrorType()

        try:
            return self.current_type.define_method(node.id, params_names, params_types, return_type, node)
        except SemanticError as e:
            self.errors.append(e)

    @visitor.when(hulk_nodes.AttributeDeclarationNode)
    def visit(self, node: hulk_nodes.AttributeDeclarationNode):
        # Set the attribute type to the declared type, ErrorType if it doesn't exist in the context or AutoType if we
        # are going to infer it
        if node.attribute_type is not None:
            try:
                attribute_type = self.context.get_type(node.attribute_type)
            except SemanticError as e:
                self.errors.append(e)
                attribute_type = ErrorType()
        else:
            attribute_type = AutoType()

        try:
            return self.current_type.define_attribute(node.id, attribute_type, node)
        except SemanticError as e:
            self.errors.append(e)

    @visitor.when(hulk_nodes.ProtocolDeclarationNode)
    def visit(self, node: hulk_nodes.ProtocolDeclarationNode):
        self.current_type = self.context.get_protocol(node.idx)
        if node.parent is not None:
            try:
                # Look for a circular dependency
                parent = self.context.get_protocol(node.parent)
                current = parent
                while current is not None:
                    if current.name == self.current_type.name:
                        self.errors.append(SemanticError('Circular dependency inheritance  :O'))
                        parent = ErrorType()
                        break
                    current = current.parent
            except SemanticError as e:
                # If the parent type is not declared, set it to ErrorType
                self.errors.append(e)
                parent = ErrorType()
            try:
                self.current_type.set_parent(parent)
            except SemanticError as e:
                # If the parent type is already set
                self.errors.append(e)

        for method in node.methods_signature:
            self.visit(method)

    @visitor.when(hulk_nodes.MethodSignatureDeclarationNode)
    def visit(self, node: hulk_nodes.MethodSignatureDeclarationNode):
        params_names, params_types = self.get_params_names_and_types(node)

        try:
            # Check if the return type is declared
            return_type = self.context.get_type_or_protocol(node.return_type)
        except SemanticError as e:
            self.errors.append(e)
            return_type = ErrorType()

        try:
            return self.current_type.define_method(node.id, params_names, params_types, return_type, node)
        except SemanticError as e:
            self.errors.append(e)
