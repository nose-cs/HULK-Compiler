import src.hulk_grammar.hulk_ast_nodes as hulk_nodes
import src.visitor as visitor
from src.errors import SemanticError

from src.semantics.semantic import Context, StringType, NumberType, BoolType, ObjectType


class TypesCollector(object):

    def __init__(self, errors) -> None:
        self.context: Context = None
        self.errors = errors

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(hulk_nodes.ProgramNode)
    def visit(self, node: hulk_nodes.ProgramNode):
        self.context = Context()
        self.context.types['String'] = StringType()
        self.context.types['Number'] = NumberType()
        self.context.types['Bool'] = BoolType()
        self.context.types['Object'] = ObjectType()
        for decl in node.declarations:
            self.visit(decl)
        return self.context, self.errors

    @visitor.when(hulk_nodes.TypeDeclarationNode)
    def visit(self, node: hulk_nodes.TypeDeclarationNode):
        try:
            self.context.create_type(node.idx)
        except SemanticError as e:
            self.errors.append(e)
            # todo what happens here when I discover an error in the type declaration

    @visitor.when(hulk_nodes.ProtocolDeclarationNode)
    def visit(self, node: hulk_nodes.ProtocolDeclarationNode):
        try:
            self.context.create_protocol(node.idx)
        except SemanticError as e:
            self.errors.append(e)
