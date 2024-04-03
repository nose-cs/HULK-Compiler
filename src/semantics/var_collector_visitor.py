import src.hulk_grammar.hulk_ast_nodes as hulk_nodes
import src.visitor as visitor
from src.errors import SemanticError
from src.semantics.types import ErrorType, AutoType, Method, SelfType
from src.semantics.utils import Scope, Context, Function


class VarCollector(object):
    def __init__(self, context, errors=None) -> None:
        if errors is None:
            errors = []
        self.context: Context = context
        self.current_type = None
        self.errors: list = errors

    @visitor.on('node')
    def visit(self, node, scope):
        pass

    @visitor.when(hulk_nodes.ProgramNode)
    def visit(self, node: hulk_nodes.ProgramNode, scope: Scope = None):
        scope = Scope()
        node.scope = scope

        for declaration in node.declarations:
            self.visit(declaration, scope.create_child())

        self.visit(node.expression, scope.create_child())

        return scope

    @visitor.when(hulk_nodes.TypeDeclarationNode)
    def visit(self, node: hulk_nodes.TypeDeclarationNode, scope: Scope):
        node.scope = scope

        self.current_type = self.context.get_type(node.idx)

        # Set parent arguments when they are None
        if node.parent_args is None and node.params_ids is not None:
            node.parent_args = []

        # Set params cause in the type builder I didn't have the params of my parent
        if node.parent_args is None and node.params_ids is None:
            self.current_type.set_params()
            node.params_ids, node.params_types = self.current_type.params_names, self.current_type.params_types
            # After this I know that my parent's args are my params (are just variables with its params names)
            node.parent_args = [hulk_nodes.VariableNode(param_name) for param_name in self.current_type.params_names]

        # Create a new scope that includes the parameters
        new_scope = scope.create_child()
        for i in range(len(self.current_type.params_names)):
            new_scope.define_variable(self.current_type.params_names[i], self.current_type.params_types[i])

        for expr in node.parent_args:
            self.visit(expr, new_scope.create_child())

        for attr in node.attributes:
            self.visit(attr, new_scope.create_child())

        # Create a new scope that includes the self symbol
        methods_scope = scope.create_child()
        methods_scope.define_variable('self', SelfType(self.current_type))
        for method in node.methods:
            self.visit(method, methods_scope.create_child())

    @visitor.when(hulk_nodes.AttributeDeclarationNode)
    def visit(self, node: hulk_nodes.AttributeDeclarationNode, scope: Scope):
        node.scope = scope

        self.visit(node.expr, scope.create_child())

    @visitor.when(hulk_nodes.MethodDeclarationNode)
    def visit(self, node: hulk_nodes.MethodDeclarationNode, scope: Scope):
        node.scope = scope

        method: Method = self.current_type.get_method(node.id)

        new_scope = scope.create_child()

        for i in range(len(method.param_names)):
            new_scope.define_variable(method.param_names[i], method.param_types[i])

        self.visit(node.expr, new_scope)

    @visitor.when(hulk_nodes.FunctionDeclarationNode)
    def visit(self, node: hulk_nodes.FunctionDeclarationNode, scope: Scope):
        node.scope = scope

        function: Function = self.context.get_function(node.id)

        new_scope = scope.create_child()

        for i in range(len(function.param_names)):
            new_scope.define_variable(function.param_names[i], function.param_types[i])

        self.visit(node.expr, new_scope)

    @visitor.when(hulk_nodes.ExpressionBlockNode)
    def visit(self, node: hulk_nodes.ExpressionBlockNode, scope: Scope):
        # block_scope = scope.create_child()
        node.scope = scope  # block_scope

        for expr in node.expressions:
            self.visit(expr, scope.create_child())

    @visitor.when(hulk_nodes.VarDeclarationNode)
    def visit(self, node: hulk_nodes.VarDeclarationNode, scope: Scope):
        node.scope = scope

        # I don't want to include the var before to avoid let a = a in print(a);
        self.visit(node.expr, scope.create_child())

        # Check if the variable type is a defined type, an error type or auto_type (we need to infer it)
        if node.var_type is not None:
            try:
                var_type = self.context.get_type_or_protocol(node.var_type)
            except SemanticError as e:
                self.errors.append(e)
                var_type = ErrorType()
        else:
            var_type = AutoType()

        scope.define_variable(node.id, var_type)

    @visitor.when(hulk_nodes.LetInNode)
    def visit(self, node: hulk_nodes.LetInNode, scope: Scope):
        node.scope = scope
        # Create a new scope for every new variable declaration to follow scoping rules
        # https://matcom.in/hulk/guide/variables/#redefining-symbols
        old_scope = scope
        for declaration in node.var_declarations:
            new_scope = old_scope.create_child()
            self.visit(declaration, new_scope)
            old_scope = new_scope

        self.visit(node.body, old_scope.create_child())

    @visitor.when(hulk_nodes.DestructiveAssignmentNode)
    def visit(self, node: hulk_nodes.DestructiveAssignmentNode, scope: Scope):
        node.scope = scope
        self.visit(node.target, scope.create_child())
        self.visit(node.expr, scope.create_child())

    @visitor.when(hulk_nodes.BinaryExpressionNode)
    def visit(self, node: hulk_nodes.BinaryExpressionNode, scope: Scope):
        node.scope = scope
        self.visit(node.left, scope.create_child())
        self.visit(node.right, scope.create_child())

    @visitor.when(hulk_nodes.UnaryExpressionNode)
    def visit(self, node: hulk_nodes.UnaryExpressionNode, scope: Scope):
        node.scope = scope
        self.visit(node.operand, scope.create_child())

    @visitor.when(hulk_nodes.ConditionalNode)
    def visit(self, node: hulk_nodes.ConditionalNode, scope: Scope):
        node.scope = scope
        for condition in node.conditions:
            self.visit(condition, scope.create_child())

        for expression in node.expressions:
            self.visit(expression, scope.create_child())

        self.visit(node.default_expr, scope.create_child())

    @visitor.when(hulk_nodes.WhileNode)
    def visit(self, node: hulk_nodes.WhileNode, scope: Scope):
        node.scope = scope
        self.visit(node.condition, scope.create_child())
        self.visit(node.expression, scope.create_child())

    @visitor.when(hulk_nodes.ForNode)
    def visit(self, node: hulk_nodes.ForNode, scope: Scope):
        node.scope = scope
        expr_scope = scope.create_child()

        expr_scope.define_variable(node.var, AutoType())

        self.visit(node.iterable, scope.create_child())
        self.visit(node.expression, expr_scope)

    @visitor.when(hulk_nodes.IsNode)
    def visit(self, node: hulk_nodes.IsNode, scope: Scope):
        node.scope = scope
        try:
            self.context.get_type_or_protocol(node.ttype)
        except SemanticError as e:
            self.errors.append(e)
            self.context.create_error_type(node.ttype)

        self.visit(node.expression, scope.create_child())

    @visitor.when(hulk_nodes.AsNode)
    def visit(self, node: hulk_nodes.AsNode, scope: Scope):
        node.scope = scope
        try:
            self.context.get_type_or_protocol(node.ttype)
        except SemanticError as e:
            self.errors.append(e)
            self.context.create_error_type(node.ttype)

        self.visit(node.expression, scope.create_child())

    @visitor.when(hulk_nodes.FunctionCallNode)
    def visit(self, node: hulk_nodes.FunctionCallNode, scope: Scope):
        node.scope = scope
        for arg in node.args:
            self.visit(arg, scope.create_child())

    @visitor.when(hulk_nodes.BaseCallNode)
    def visit(self, node: hulk_nodes.BaseCallNode, scope: Scope):
        node.scope = scope
        for arg in node.args:
            self.visit(arg, scope.create_child())

    @visitor.when(hulk_nodes.AttributeCallNode)
    def visit(self, node: hulk_nodes.AttributeCallNode, scope: Scope):
        node.scope = scope
        self.visit(node.obj, scope.create_child())

    @visitor.when(hulk_nodes.MethodCallNode)
    def visit(self, node: hulk_nodes.MethodCallNode, scope: Scope):
        node.scope = scope
        self.visit(node.obj, scope.create_child())
        for arg in node.args:
            self.visit(arg, scope.create_child())

    @visitor.when(hulk_nodes.TypeInstantiationNode)
    def visit(self, node: hulk_nodes.TypeInstantiationNode, scope: Scope):
        node.scope = scope
        for arg in node.args:
            self.visit(arg, scope.create_child())

    @visitor.when(hulk_nodes.VariableNode)
    def visit(self, node: hulk_nodes.VariableNode, scope: Scope):
        node.scope = scope

    @visitor.when(hulk_nodes.VectorInitializationNode)
    def visit(self, node: hulk_nodes.VectorInitializationNode, scope: Scope):
        node.scope = scope
        for element in node.elements:
            self.visit(element, scope.create_child())

    @visitor.when(hulk_nodes.VectorComprehensionNode)
    def visit(self, node: hulk_nodes.VectorComprehensionNode, scope: Scope):
        node.scope = scope

        selector_scope = scope.create_child()
        selector_scope.define_variable(node.var, AutoType())
        self.visit(node.selector, selector_scope)

        self.visit(node.iterable, scope.create_child())

    @visitor.when(hulk_nodes.IndexingNode)
    def visit(self, node: hulk_nodes.IndexingNode, scope: Scope):
        node.scope = scope

        self.visit(node.obj, scope.create_child())
        self.visit(node.index, scope.create_child())

    @visitor.when(hulk_nodes.ConstantBoolNode)
    def visit(self, node: hulk_nodes.ConstantBoolNode, scope: Scope):
        node.scope = scope

    @visitor.when(hulk_nodes.ConstantNumNode)
    def visit(self, node: hulk_nodes.ConstantNumNode, scope: Scope):
        node.scope = scope

    @visitor.when(hulk_nodes.ConstantStringNode)
    def visit(self, node: hulk_nodes.ConstantStringNode, scope: Scope):
        node.scope = scope
