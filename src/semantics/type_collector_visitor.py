import src.hulk_grammar.hulk_ast_nodes as hulk_nodes
import src.visitor as visitor
from src.errors import SemanticError

from src.semantics.utils import Context


class TypeCollector(object):

    def __init__(self, errors) -> None:
        self.context = None
        self.errors = errors

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(hulk_nodes.ProgramNode)
    def visit(self, node: hulk_nodes.ProgramNode):
        # Create the global context
        self.context = Context()

        # Add the basic types
        object_type = self.context.create_type('Object')

        string_type = self.context.create_type('String')
        string_type.set_parent(object_type)

        number_type = self.context.create_type('Number')
        number_type.set_parent(object_type)

        bool_type = self.context.create_type('Bool')
        bool_type.set_parent(object_type)

        # Add the built-in functions
        self.context.create_function('print', ['value'], [object_type], string_type)
        self.context.create_function('sqrt', ['value'], [number_type], number_type)
        self.context.create_function('sin', ['angle'], [number_type], number_type)
        self.context.create_function('cos', ['angle'], [number_type], number_type)
        self.context.create_function('exp', ['value'], [number_type], number_type)
        self.context.create_function('log', ['base', 'value'], [number_type, number_type], number_type)
        self.context.create_function('rand', [], [], number_type)

        for decl in node.declarations:
            self.visit(decl)
        return self.context, self.errors

    @visitor.when(hulk_nodes.TypeDeclarationNode)
    def visit(self, node: hulk_nodes.TypeDeclarationNode):
        try:
            self.context.create_type(node.idx)
        except SemanticError as e:
            self.errors.append(e)

    @visitor.when(hulk_nodes.ProtocolDeclarationNode)
    def visit(self, node: hulk_nodes.ProtocolDeclarationNode):
        try:
            self.context.create_protocol(node.idx)
        except SemanticError as e:
            self.errors.append(e)
