import src.hulk_grammar.hulk_ast_nodes as hulk_nodes
import src.visitor as visitor


class FormatVisitor(object):
    @visitor.on('node')
    def visit(self, node, tabs):
        pass

    @visitor.when(hulk_nodes.ProgramNode)
    def visit(self, node: hulk_nodes.ProgramNode, tabs=0):
        ans = '\t' * tabs + f'\\__ProgramNode [<stat>; ... <stat>;]'
        declarations = '\n'.join(self.visit(decl, tabs + 1) for decl in node.declarations)
        expression = self.visit(node.expression, tabs + 1)
        return f'{ans}\n{declarations}\n{expression}'

    @visitor.when(hulk_nodes.VarDeclarationNode)
    def visit(self, node: hulk_nodes.VarDeclarationNode, tabs=0):
        ans = '\t' * tabs + f'\\__VarDeclarationNode: let {node.id} = <expr>'
        expr = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{expr}'

    @visitor.when(hulk_nodes.FunctionDeclarationNode)
    def visit(self, node: hulk_nodes.FunctionDeclarationNode, tabs=0):
        params = ', '.join(node.params)
        ans = '\t' * tabs + f'\\__FuncDeclarationNode: def {node.id}({params}) -> <expr>'
        body = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{body}'

    @visitor.when(hulk_nodes.BinaryExpressionNode)
    def visit(self, node: hulk_nodes.BinaryExpressionNode, tabs=0):
        ans = '\t' * tabs + f'\\__<expr> {node.__class__.__name__} <expr>'
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        return f'{ans}\n{left}\n{right}'

    @visitor.when(hulk_nodes.AtomicNode)
    def visit(self, node: hulk_nodes.AtomicNode, tabs=0):
        return '\t' * tabs + f'\\__ {node.__class__.__name__}: {node.lex}'

    @visitor.when(hulk_nodes.CallNode)
    def visit(self, node: hulk_nodes.CallNode, tabs=0):
        ans = '\t' * tabs + f'\\__CallNode: {node.lex}(<expr>, ..., <expr>)'
        args = '\n'.join(self.visit(arg, tabs + 1) for arg in node.args)
        return f'{ans}\n{args}'

    @visitor.when(hulk_nodes.EqualNode)
    def visit(self, node: hulk_nodes.EqualNode, tabs=0):
        ans = '\t' * tabs + f'\\__EqualNode: <expr> == <expr>'
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        return f'{ans}\n{left}\n{right}'

    @visitor.when(hulk_nodes.PlusNode)
    def visit(self, node: hulk_nodes.PlusNode, tabs=0):
        ans = '\t' * tabs + f'\\__PlusNode: <expr> + <expr>'
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        return f'{ans}\n{left}\n{right}'
