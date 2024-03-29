import src.visitor as visitor
import src.hulk_grammar.hulk_ast_nodes as hulk_nodes
from src.semantics.semantic import Context, Type

class CodeGenC(object):

    def __init__(self, context) -> None:
        self.context: Context = context

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(hulk_nodes.TypeInstantiationNode)
    def visit(self, node: hulk_nodes.TypeInstantiationNode):
        code = "create" + node.idx + "("
        before = len(code)

        for arg in node.args:
            code += self.visit(arg) + ", "

        current: Type = self.context.get_type(node.idx)

        while current is not None:
            if len(current.node.parent_args) > 0:
                for arg in current.node.parent_args:
                    code += self.visit(arg) + ", "
            elif current.parent is not None:
                for i in range(len(current.parent.params_names)):
                    code += "NULL" + ", "

            current = current.parent

        if before != len(code):
            code = code[:-2]
        
        return code

    @visitor.when(hulk_nodes.MethodDeclarationNode)
    def visit(self, node: hulk_nodes.MethodDeclarationNode):
        return self.visit(node.expr)

    @visitor.when(hulk_nodes.FunctionDeclarationNode)
    def visit(self, node: hulk_nodes.FunctionDeclarationNode):
        return self.visit(node.expr)

    @visitor.when(hulk_nodes.ExpressionBlockNode)
    def visit(self, node: hulk_nodes.ExpressionBlockNode):
        code = ""

        for expression in node.expressions:
            code += self.visit(expression) + ";\n"

        return code
    
    @visitor.when(hulk_nodes.PlusNode)
    def visit(self, node: hulk_nodes.PlusNode):
        return "numberSum(" + self.visit(node.left) + ", " + self.visit(node.right) + ")"

    @visitor.when(hulk_nodes.VariableNode)
    def visit(self, node: hulk_nodes.VariableNode):
        return self.context[node.lex]