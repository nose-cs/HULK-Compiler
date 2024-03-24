import src.hulk_grammar.hulk_ast_nodes as hulk_nodes
import src.visitor as visitor
from global_Context import GlobalContext
from type import Type
import type
class Methods_Visitor(object):

    def __init__(self, context:GlobalContext, errors = []) -> None:
        self.context:GlobalContext = context
        self.curent_type:Type = None
        self.errors:list = errors

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(hulk_nodes.ProgramNode)
    def visit(self, node: hulk_nodes.ProgramNode):
        for decl in node.declarations:
            self.visit(decl)


    @visitor.when(hulk_nodes.TypeDeclarationNode)
    def visit(self, node: hulk_nodes.TypeDeclarationNode):
        self.curent_type = self.context.types[node.idx]
        if(node.parent is not None):
            if(node.parent in ['Int' , 'Bool' , 'String', 'Self']):
                self.errors.append(f'Type {node.idx} is inheriting from a forbiden type')
                if not node.parent in self.context.types:
                    self.errors.append(f'Type {node.idx} is inheriting from an undeclared type')
                else:
                    parent = self.context.types[node.parent]
                    current = parent
                    while(current is not None):
                        if current.parent == self.curent_type.id:
                            self.errors.append['Circular dependency inheritence']
                            parent = type.ErrorType()
                            break
                    self.curent_type.parent = parent
        for member in node.body:
            self.visit(member)


    @visitor.when(hulk_nodes.MethodDeclarationNode)
    def visit(self, node: hulk_nodes.MethodDeclarationNode):
        