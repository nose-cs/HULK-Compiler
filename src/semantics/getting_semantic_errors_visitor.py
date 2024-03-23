import src.hulk_grammar.hulk_ast_nodes as hulk_nodes
import src.visitor as visitor
from scope import Scope


class SemanticErrorVisitor(object):
    @visitor.on('node')
    def visit(self, node, scope, types, functions):
        pass

    @visitor.when(hulk_nodes.ProgramNode)
    def visit(self, node: hulk_nodes.ProgramNode, scope:Scope, types , functions):
        errors = []
        for declaration in node.declarations:
            errors.append(self.visit(declaration, scope, types, functions))
        errors.append(self.visit(node.expression))
        return errors

    @visitor.when(hulk_nodes.VarDeclarationNode)
    def visit(self, node: hulk_nodes.VarDeclarationNode, scope:Scope, types, functions):
        if scope.IsDefined(node.id):
            return [f'The variable {node.id} is alredy declarated :(']
        scope.define(node.id)
        return []
    

    @visitor.when(hulk_nodes.LetInNode)
    def visit(self, node: hulk_nodes.LetInNode, scope:Scope, types, functions):
        errors = []
        newScope = scope.newContext
        for declaration in node.var_declarations:
            errors.append(self.visit(declaration, newScope, types, functions))
        errors.append(self.visit(declaration, newScope, types, functions)) 
        return errors

    @visitor.when(hulk_nodes.DestructiveAssignmentNode)
    def visit(self, node: hulk_nodes.DestructiveAssignmentNode, scope:Scope, types, functions):
        return [] if scope.isDefined(node.id) else [f'The variable {node.id} is not defined in this Scope T_T']
            
 
