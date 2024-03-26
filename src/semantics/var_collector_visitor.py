import src.hulk_grammar.hulk_ast_nodes as hulk_nodes
import src.visitor as visitor
from src.errors import SemanticError
from src.semantics.semantic import Scope, Context, ErrorType, AutoType, SelfType


# todo: i am calling scope.define_variable() in a bad way
#  I dont need to check protocols or atomic nodes looking for variable declarations


class VariablesCollectorVisitor(object):
    def __init__(self, context, errors=None) -> None:
        if errors is None:
            errors = []
        self.context: Context = context
        self.current_type = None
        self.errors: list = errors

    @visitor.on('node')
    def visit(self, node, scope, types, functions):
        pass

    @visitor.when(hulk_nodes.ProgramNode)
    def visit(self, node: hulk_nodes.ProgramNode, scope: Scope):
        for declaration in node.declarations:
            self.visit(declaration, scope.create_child())

        self.visit(node.expression)

    @visitor.when(hulk_nodes.TypeDeclarationNode)
    def visit(self, node: hulk_nodes.TypeDeclarationNode, scope: Scope):
        self.current_type = self.context.get_type(node.idx)
        # Create a new scope that includes the parameters
        new_scope = scope.create_child()

        for i in range(self.current_type.params_names):
            try:
                scope.define_variable(self.current_type.params_names[i], self.current_type.params_types[i])
            except SemanticError as e:
                self.errors.append(e)

        for expr in node.parent_args:
            self.visit(expr, new_scope)

        for attr in node.attributes:
            self.visit(attr, new_scope)

        # add self.current_types.attributes here ??

        # todo check this, is self.attr a variable?
        new_scope.define_variable('self', SelfType())

        for method in node.methods:
            self.visit(method, new_scope)

    @visitor.when(hulk_nodes.AttributeDeclarationNode)
    def visit(self, node: hulk_nodes.AttributeDeclarationNode, scope: Scope):
        self.visit(node.expr, scope)

    @visitor.when(hulk_nodes.MethodDeclarationNode)
    def visit(self, node: hulk_nodes.MethodDeclarationNode, scope: Scope):
        method = self.current_type.get_method(node.id)

        new_scope = scope.create_child()

        for i in range(len(method.params_names)):
            try:
                new_scope.define_variable(method.params_names[i], method.params_types[i])
            except SemanticError as e:
                # todo can put a more specific error message
                self.errors.append(e)

        self.visit(node.expr, new_scope)

    @visitor.when(hulk_nodes.FunctionDeclarationNode)
    def visit(self, node: hulk_nodes.FunctionDeclarationNode, scope: Scope):
        function = self.context.get_function(node.id)

        new_scope = scope.create_child()

        for i in range(len(function.params_names)):
            try:
                new_scope.define_variable(function.params_names[i], function.params_types[i])
            except SemanticError as e:
                # todo can put a more specific error message
                self.errors.append(e)

        self.visit(node.expr, new_scope)

    @visitor.when(hulk_nodes.ExpressionBlockNode)
    def visit(self, node: hulk_nodes.ExpressionBlockNode, scope: Scope):
        for expr in node.expressions:
            self.visit(expr, scope)

    @visitor.when(hulk_nodes.VarDeclarationNode)
    def visit(self, node: hulk_nodes.VarDeclarationNode, scope: Scope):
        # I don't want to include the var before to avoid let a = a in print(a);
        self.visit(node.expr, scope)

        # Check if the variable type is a defined type, an error type or auto_type (we need to infer it)
        if node.var_type is not None:
            try:
                var_type = self.context.get_type_or_protocol(node.var_type)
            except SemanticError as e:
                self.errors.append(e)
                var_type = ErrorType()
        else:
            var_type = AutoType()

        try:
            scope.define_variable(node.id, var_type)
        except SemanticError as e:
            self.errors.append(e)

    @visitor.when(hulk_nodes.LetInNode)
    def visit(self, node: hulk_nodes.LetInNode, scope: Scope):
        new_scope = scope.create_child()

        for declaration in node.var_declarations:
            self.visit(declaration, new_scope)

        self.visit(node.body, new_scope)

    @visitor.when(hulk_nodes.DestructiveAssignmentNode)
    def visit(self, node: hulk_nodes.DestructiveAssignmentNode, scope: Scope):
        self.visit(node.expr, scope)

    @visitor.when(hulk_nodes.BinaryExpressionNode)
    def visit(self, node: hulk_nodes.BinaryExpressionNode, scope: Scope):
        self.visit(node.left, scope)
        self.visit(node.right, scope)

    @visitor.when(hulk_nodes.UnaryExpressionNode)
    def visit(self, node: hulk_nodes.UnaryExpressionNode, scope: Scope):
        self.visit(node.operand, scope)

    @visitor.when(hulk_nodes.ConditionalNode)
    def visit(self, node: hulk_nodes.ConditionalNode, scope: Scope):
        for condition in node.conditions:
            self.visit(condition, scope.create_child())

        for expression in node.expressions:
            self.visit(expression, scope.create_child())

        self.visit(node.default_expr, scope.create_child())

    @visitor.when(hulk_nodes.WhileNode)
    def visit(self, node: hulk_nodes.WhileNode, scope: Scope):
        self.visit(node.condition, scope.create_child())
        self.visit(node.expression, scope.create_child())

    @visitor.when(hulk_nodes.ForNode)
    def visit(self, node: hulk_nodes.ForNode, scope: Scope):
        new_scope = scope.create_child()
        # todo: fill this

    # todo vector initialization

    @visitor.when(hulk_nodes.IsNode)
    def visit(self, node: hulk_nodes.IsNode, scope: Scope):
        self.visit(node.expression, scope)

    @visitor.when(hulk_nodes.AsNode)
    def visit(self, node: hulk_nodes.AsNode, scope: Scope):
        self.visit(node.expression, scope)

    @visitor.when(hulk_nodes.FunctionCallNode)
    def visit(self, node: hulk_nodes.FunctionCallNode, scope: Scope):
        for arg in node.args:
            self.visit(arg, scope)

    @visitor.when(hulk_nodes.MethodCallNode)
    def visit(self, node: hulk_nodes.MethodCallNode, scope: Scope):
        for arg in node.args:
            self.visit(arg, scope)
