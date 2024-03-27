import src.hulk_grammar.hulk_ast_nodes as hulk_nodes
import src.visitor as visitor


class FormatterVisitor(object):
    @visitor.on('node')
    def visit(self, node, tabs):
        pass

    @visitor.when(hulk_nodes.ProgramNode)
    def visit(self, node: hulk_nodes.ProgramNode, tabs=0):
        ans = '\t' * tabs + f'\\__ ProgramNode [<stat>; ... <stat> <expr>;]'
        declarations = '\n'.join(self.visit(decl, tabs + 1) for decl in node.declarations)
        expression = self.visit(node.expression, tabs + 1)
        return f'{ans}\n{declarations}\n{expression}'

    @visitor.when(hulk_nodes.FunctionDeclarationNode)
    def visit(self, node: hulk_nodes.FunctionDeclarationNode, tabs=0):
        params = ', '.join(
            [f'{node.params_ids[i]}' + f': {node.params_types[i]}' if node.params_types[i] is not None else '' for i in
             range(len(node.params_ids))])
        ans = '\t' * tabs + f'\\__ FuncDeclarationNode: def {node.id}({params}) -> <expr>'
        body = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{body}'

    @visitor.when(hulk_nodes.TypeDeclarationNode)
    def visit(self, node: hulk_nodes.TypeDeclarationNode, tabs=0):
        params = ', '.join(
            [f'{node.params_ids[i]}' + f': {node.params_types[i]}' if node.params_types[i] is not None else '' for i in
             range(len(node.params_ids))])
        parent = f": {node.parent}({', '.join(node.parent_args)})" if node.parent else ""
        ans = '\t' * tabs + f'\\__ TypeDeclarationNode: type {node.idx}({params}){parent} -> <body>'
        attributes = '\n'.join([self.visit(attr, tabs + 1) for attr in node.attributes])
        methods = '\n'.join([self.visit(method, tabs + 1) for method in node.methods])
        return f'{ans}\n{attributes}\n{methods}'

    @visitor.when(hulk_nodes.MethodDeclarationNode)
    def visit(self, node: hulk_nodes.MethodDeclarationNode, tabs=0):
        params = ', '.join(
            [f'{node.params_ids[i]}' + f': {node.params_types[i]}' if node.params_types[i] is not None else '' for i in
             range(len(node.params_ids))])
        ans = '\t' * tabs + f'\\__ MethodDeclarationNode: {node.id}({params}) -> <expr>'
        body = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{body}'

    @visitor.when(hulk_nodes.ProtocolDeclarationNode)
    def visit(self, node: hulk_nodes.ProtocolDeclarationNode, tabs=0):
        methods = '\n'.join(self.visit(decl, tabs + 1) for decl in node.methods_signature)
        parent = f": {node.parent}" if node.parent else ""
        ans = '\t' * tabs + f'\\__ ProtocolDeclarationNode: protocol {node.idx}{parent} -> <body>'
        return f'{ans}\n{methods}'

    @visitor.when(hulk_nodes.MethodSignatureDeclarationNode)
    def visit(self, node: hulk_nodes.MethodSignatureDeclarationNode, tabs=0):
        params = ', '.join([f'{node.params_ids[i]}' + f': {node.params_types[i]}' for i in range(len(node.params_ids))])
        ans = '\t' * tabs + f'\\__ MethodDeclarationNode: {node.id}({params}):{node.return_type}'
        return f'{ans}'

    @visitor.when(hulk_nodes.AttributeDeclarationNode)
    def visit(self, node: hulk_nodes.AttributeDeclarationNode, tabs=0):
        ttype = f": {node.attribute_type}" if node.attribute_type is not None else ""
        ans = '\t' * tabs + f'\\__ AttributeStatementNode: {node.id}{ttype} = <expr>'
        body = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{body}'

    @visitor.when(hulk_nodes.BinaryExpressionNode)
    def visit(self, node: hulk_nodes.BinaryExpressionNode, tabs=0):
        ans = '\t' * tabs + f'\\__ <expr> {node.__class__.__name__} <expr>'
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        return f'{ans}\n{left}\n{right}'

    @visitor.when(hulk_nodes.AtomicNode)
    def visit(self, node: hulk_nodes.AtomicNode, tabs=0):
        return '\t' * tabs + f'\\__ {node.__class__.__name__}: {node.lex}'

    @visitor.when(hulk_nodes.UnaryExpressionNode)
    def visit(self, node: hulk_nodes.UnaryExpressionNode, tabs=0):
        return '\t' * tabs + f'\\__ {node.__class__.__name__}: {node.operand}'

    @visitor.when(hulk_nodes.LetInNode)
    def visit(self, node: hulk_nodes.LetInNode, tabs=0):
        ans = '\t' * tabs + f'\\__ LetInNode: let [<var>, ..., <var>] in <expr>'
        variables = '\n'.join(self.visit(var, tabs + 1) for var in node.var_declarations)
        expr = self.visit(node.body, tabs + 1)
        return f'{ans}\n{variables}\n{expr}'

    @visitor.when(hulk_nodes.VarDeclarationNode)
    def visit(self, node: hulk_nodes.VarDeclarationNode, tabs=0):
        ans = '\t' * tabs + f'\\__ VarDeclarationNode: {node.id} = <expr>'
        expr = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{expr}'

    @visitor.when(hulk_nodes.FunctionCallNode)
    def visit(self, node: hulk_nodes.FunctionCallNode, tabs=0):
        ans = '\t' * tabs + f'\\__ CallNode: {node.idx}(<expr>, ..., <expr>)'
        args = '\n'.join(self.visit(arg, tabs + 1) for arg in node.args)
        return f'{ans}\n{args}'

    @visitor.when(hulk_nodes.TypeInstantiationNode)
    def visit(self, node: hulk_nodes.TypeInstantiationNode, tabs=0):
        ans = '\t' * tabs + f'\\__ TypeInstantiationNode: {node.idx}(<expr>, ..., <expr>)'
        args = '\n'.join(self.visit(arg, tabs + 1) for arg in node.args)
        return f'{ans}\n{args}'

    @visitor.when(hulk_nodes.ExpressionBlockNode)
    def visit(self, node: hulk_nodes.ExpressionBlockNode, tabs=0):
        ans = '\t' * tabs + f'\\__ ExpressionBlockNode [<expr>; ... <expr>;]'
        expressions = '\n'.join(self.visit(decl, tabs + 1) for decl in node.expressions)
        return f'{ans}\n{expressions}'

    @visitor.when(hulk_nodes.DestructiveAssignmentNode)
    def visit(self, node: hulk_nodes.DestructiveAssignmentNode, tabs=0):
        ans = '\t' * tabs + f'\\__ DestructiveAssignmentNode: {node.id} := <expr>'
        expr = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{expr}'

    @visitor.when(hulk_nodes.WhileNode)
    def visit(self, node: hulk_nodes.WhileNode, tabs=0):
        ans = '\t' * tabs + f'\\__ WhileNode: while(<expr>) <expr>'
        cond = self.visit(node.condition)
        expr = self.visit(node.expression, tabs + 1)
        return f'{ans}\n{cond}\n{expr}'

    @visitor.when(hulk_nodes.ForNode)
    def visit(self, node: hulk_nodes.ForNode, tabs=0):
        ans = '\t' * tabs + f'\\__ ForNode: for({node.var} in <expr>) <expr>'
        iterable = self.visit(node.iterable)
        expr = self.visit(node.expression, tabs + 1)
        return f'{ans}\n{iterable}\n{expr}'

    @visitor.when(hulk_nodes.ConditionalNode)
    def visit(self, node: hulk_nodes.ConditionalNode, tabs=0):
        ans = '\t' * tabs + f'\\__ ConditionalNode:'

        conditions = [self.visit(cond, tabs + 1) for cond in node.conditions]
        expressions = [self.visit(expr, tabs + 1) for expr in node.expressions]
        cond_expr = zip(conditions, expressions)

        if_cond, if_expr = cond_expr[0]
        if_clause = '\t' * tabs + f'\\__ if(<expr>) <expr>\n{if_cond}\n{if_expr}'

        cond_exp = cond_expr[1:]

        elif_clauses = ['\t' * tabs + f'\\__ elif(<expr>) <expr>\n{cond}\n{expr}' for (cond, expr) in cond_exp]
        elif_clauses = '\n' + '\n'.join(elif_clauses) if len(elif_clauses) > 0 else ''

        else_clause = '\t' * tabs + f'\\__ else <expr>\n{self.visit(node.default_expr, tabs + 1)}'

        return f'{ans}\n{if_clause}{elif_clauses}\n{else_clause}'

    @visitor.when(hulk_nodes.AsNode)
    def visit(self, node: hulk_nodes.AsNode, tabs=0):
        ans = '\t' * tabs + f'\\__ AsNode: <expr> as {node.ttype}'
        expr = self.visit(node.expression, tabs + 1)
        return f'{ans}\n{expr}'

    @visitor.when(hulk_nodes.IsNode)
    def visit(self, node: hulk_nodes.IsNode, tabs=0):
        ans = '\t' * tabs + f'\\__ IsNode: <expr> is {node.ttype}'
        expr = self.visit(node.expression, tabs + 1)
        return f'{ans}\n{expr}'

    @visitor.when(hulk_nodes.VectorInitializationNode)
    def visit(self, node: hulk_nodes.VectorInitializationNode, tabs=0):
        ans = '\t' * tabs + f'\\__ VectorInitializationNode: [<expr>, ..., <expr>]'
        elements = '\n'.join(self.visit(element, tabs + 1) for element in node.elements)
        return f'{ans}\n{elements}'

    @visitor.when(hulk_nodes.VectorComprehensionNode)
    def visit(self, node: hulk_nodes.VectorComprehensionNode, tabs=0):
        ans = '\t' * tabs + f'\\__ VectorComprehensionNode: [<expr> || {node.var} in <expr>]'
        selector = self.visit(node.selector, tabs + 1)
        iterable = self.visit(node.iterable, tabs + 1)
        return f'{ans}\n{selector}\n{iterable}'

    @visitor.when(hulk_nodes.AttributeCallNode)
    def visit(self, node: hulk_nodes.AttributeCallNode, tabs=0):
        ans = '\t' * tabs + f'\\__ AttributeCallNode: <expr>.{node.attribute}'
        obj = self.visit(node.obj, tabs + 1)
        return f'{ans}\n{obj}'

    @visitor.when(hulk_nodes.MethodCallNode)
    def visit(self, node: hulk_nodes.MethodCallNode, tabs=0):
        ans = '\t' * tabs + f'\\__ MethodCallNode: <expr>.{node.method}(<expr>, ..., <expr>)'
        obj = self.visit(node.obj, tabs + 1)
        args = '\n'.join(self.visit(arg, tabs + 1) for arg in node.args)
        return f'{ans}\n{obj}\n{args}'
