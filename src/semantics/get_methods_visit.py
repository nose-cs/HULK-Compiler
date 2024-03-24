import src.hulk_grammar.hulk_ast_nodes as hulk_nodes
import src.visitor as visitor
from global_Context import GlobalContext
from type import Type
import type
import method
class Methods_Visitor(object):

    def __init__(self, context:GlobalContext, errors = []) -> None:
        self.context:GlobalContext = context
        self.curent_type:Type = None
        self.errors:list = errors
        self.current_method:method.method = None

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
                self.errors.append(f'Type {node.idx} is inheriting from a forbiden type  -_- ')
                if not node.parent in self.context.types:
                    self.errors.append(f'Type {node.idx} is inheriting from an undeclared type  T_T')
                else:
                    parent = self.context.types[node.parent]
                    current = parent
                    while(current is not None):
                        if current.parent == self.curent_type.id:
                            self.errors.append['Circular dependency inheritence  :O']
                            parent = type.ErrorType()
                            break
                    self.curent_type.parent = parent
        for member in node.body:
            self.visit(member)


    @visitor.when(hulk_nodes.MethodDeclarationNode)
    def visit(self, node: hulk_nodes.MethodDeclarationNode):
        self.current_method = method.method(node.id)
        if(node.id in self.curent_type.methods):
            self.errors.append(f'Method {node.id} is defined more than once in the same type  D`:')
            return
        self.curent_type.methods[node.id] = self.current_method
        for param in node.params:
            self.visit(param)
        if not node.return_type in self.context.types:
            self.errors.append('Undefined return type (._. )')
        else:
            self.current_method.return_type = self.context.types[node.return_type]

    @visitor.when(hulk_nodes.ParamNode)
    def visit(self, node:hulk_nodes.ParamNode):
        if node.id in self.current_method.params_id:
            self.errors.append('A method cannot have two params with the same id')
        else: 
            self.current_method.params_id.append(node.id)
            if(node.var_type in self.context.types): self.current_method.params_types.append(node.var_type)
            else: 
                self.errors.append('Undeclared Param Type')
                self.current_method.params_types.append(type.ErrorType())
                

