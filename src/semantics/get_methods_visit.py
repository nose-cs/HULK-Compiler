import src.hulk_grammar.hulk_ast_nodes as hulk_nodes
import src.visitor as visitor


class FormatVisitor(object):
    @visitor.on('node')
    def visit(self, node, tabs):
        pass

    @visitor.when(hulk_nodes.ProgramNode)
    def visit(self, node: hulk_nodes.ProgramNode):
        function_declarations = {}
        for decl in node.declarations:
            function_declarations.update(self.visit(decl))
        return function_declarations

    @visitor.when(hulk_nodes.TypeDeclarationNode)
    def visit(self, node: hulk_nodes.TypeDeclarationNode):
        function_declarations = {}
        for func in node.body:
            function_declarations.add(self.visit(func))
        return function_declarations

    @visitor.when(hulk_nodes.FunctionDeclarationNode)
    def visit(self, node: hulk_nodes.FunctionDeclarationNode):
        return (node.id, len(node.args))