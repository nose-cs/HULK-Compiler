import src.hulk_grammar.hulk_ast_nodes as hulk_nodes
import src.visitor as visitor
from global_Context import GlobalContext 
import type

class Types_Visitor(object):


    def __init__(self) -> None:
        self.context = None
        self.errorsList = []

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(hulk_nodes.ProgramNode)
    def visit(self, node: hulk_nodes.ProgramNode):
        self.context = GlobalContext()
        self.context.types['String'] = type.StringType()
        self.context.types['Number'] = type.NumberType()
        self.context.types['Bool'] = type.BoolType()
        self.context.types['Object'] = type.ObjectType()
        for decl in node.declarations:
            self.visit(decl)
        return self.context , self.errorsList 

    @visitor.when(hulk_nodes.TypeDeclarationNode)
    def visit(self, node: hulk_nodes.TypeDeclarationNode):
        self.errorsList.append(self.context.define_type(node))

    @visitor.when(hulk_nodes.FunctionDeclarationNode)
    def visit(self, node: hulk_nodes.FunctionDeclarationNode):
        self.errorsList.append(self.context.define_function(node))

    @visitor.when(hulk_nodes.ProtocolDeclaration)
    def visit(self, node: hulk_nodes.ProtocolDeclaration):
        self.errorsList.append(self.context.ed)