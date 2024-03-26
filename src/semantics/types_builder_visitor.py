import src.hulk_grammar.hulk_ast_nodes as hulk_nodes
import src.visitor as visitor
from src.errors import SemanticError
from src.semantics.semantic import Context, ErrorType


class TypesBuilder(object):
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

        try:
            # Check if the return type is declared
            return_type = self.context.get_type_or_protocol(node.return_type)
        except SemanticError as e:
            self.errors.append(e)
            return_type = ErrorType()

        try:
            return self.context.create_function(node.id, params_names, params_types, return_type)
        except SemanticError as e:
            self.errors.append(e)

    def get_params_names_and_types(self, node):
        params_names = []
        params_types = []

        # Check that params are not repeated
        if len(node.params_ids) != len(set(node.params_ids)):
            self.errors.append(SemanticError('A function cannot have two parameters with the same name'))

        for i in range(len(node.params_ids)):
            # If the param is already declared, skip it
            if node.params_ids[i] in params_names:
                continue
            try:
                # todo check this
                if node.params_types[i] is None:
                    param_type = None
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
        self.current_type = self.context.types[node.idx]

        params_names, params_types = self.get_params_names_and_types(node)
        self.current_type.set_params(params_names, params_types)

        # Check if the type is inheriting from a forbidden type
        if node.parent in ['Number', 'Bool', 'String', 'Self']:
            self.errors.append(SemanticError(f'Type {node.idx} is inheriting from a forbidden type  -_- '))
        elif node.parent is not None:
            try:
                # Look for a circular dependency
                parent = self.context.get_type(node.parent)
                current = parent
                while current is not None:
                    if current.parent.name == self.current_type.name:
                        self.errors.append(SemanticError('Circular dependency inheritance  :O'))
                    parent = ErrorType()
                    break
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
            self.current_type.set_parent(self.context.get_type('Object'))

        for member in node.body:
            self.visit(member)

    @visitor.when(hulk_nodes.MethodDeclarationNode)
    def visit(self, node: hulk_nodes.MethodDeclarationNode):
        params_names, params_types = self.get_params_names_and_types(node)

        try:
            # Check if the return type is declared
            return_type = self.context.get_type_or_protocol(node.return_type)
        except SemanticError as e:
            self.errors.append(e)
            return_type = ErrorType()

        try:
            return self.current_type.define_method(node.id, params_names, params_types, return_type)
        except SemanticError as e:
            self.errors.append(e)

    @visitor.when(hulk_nodes.AttributeDeclarationNode)
    def visit(self, node: hulk_nodes.AttributeDeclarationNode):
        if node.attribute_type is not None:
            try:
                attribute_type = self.context.get_type(node.attribute_type)
            except SemanticError as e:
                # If the attribute type is not declared, set it to ErrorType
                self.errors.append(e)
                attribute_type = ErrorType()
        else:
            # todo check this
            attribute_type = None

        try:
            return self.current_type.define_attribute(node.id, attribute_type)
        except SemanticError as e:
            self.errors.append(e)

    @visitor.when(hulk_nodes.ProtocolDeclarationNode)
    def visit(self, node: hulk_nodes.ProtocolDeclarationNode):
        self.current_type = self.context.protocols[node.idx]

        # todo Check parents ??

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
            return self.current_type.define_method(node.id, params_names, params_types, return_type)
        except SemanticError as e:
            self.errors.append(e)
