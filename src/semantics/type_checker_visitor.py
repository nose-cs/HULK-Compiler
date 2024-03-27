import src.hulk_grammar.hulk_ast_nodes as hulk_nodes
import src.semantics.types as types
import src.visitor as visitor
from src.errors import SemanticError
from src.semantics.types import Method
from src.semantics.utils import Scope, Context, Function


class TypeChecker(object):
    def __init__(self, context, errors=None) -> None:
        if errors is None:
            errors = []
        self.context: Context = context
        self.current_type = None
        self.current_method = None
        self.errors: list = errors

    @visitor.on('node')
    def visit(self, node, scope):
        pass

    @visitor.when(hulk_nodes.ProgramNode)
    def visit(self, node: hulk_nodes.ProgramNode, scope: Scope = None):
        scope = Scope()

        for declaration in node.declarations:
            self.visit(declaration, scope.create_child())

        self.visit(node.expression, scope)

        return scope

    @visitor.when(hulk_nodes.TypeDeclarationNode)
    def visit(self, node: hulk_nodes.TypeDeclarationNode, scope: Scope):
        self.current_type = self.context.get_type(node.idx)

        # Create a new scope that includes the parameters
        new_scope = scope.create_child()
        for i in range(len(self.current_type.params_names)):
            new_scope.define_variable(self.current_type.params_names[i], self.current_type.params_types[i])

        for expr in node.parent_args:
            self.visit(expr, new_scope)

        for attr in node.attributes:
            self.visit(attr, new_scope)

        # Create a new scope that includes the self symbol
        methods_scope = scope.create_child()
        methods_scope.define_variable('self', self.current_type)
        for method in node.methods:
            self.visit(method, methods_scope)

    @visitor.when(hulk_nodes.AttributeDeclarationNode)
    def visit(self, node: hulk_nodes.AttributeDeclarationNode, scope: Scope):
        self.visit(node.expr, scope)

    @visitor.when(hulk_nodes.MethodDeclarationNode)
    def visit(self, node: hulk_nodes.MethodDeclarationNode, scope: Scope):
        method: Method = self.current_type.get_method(node.id)

        new_scope = scope.create_child()

        for i in range(len(method.param_names)):
            new_scope.define_variable(method.param_names[i], method.param_types[i])

        self.visit(node.expr, new_scope)

    @visitor.when(hulk_nodes.FunctionDeclarationNode)
    def visit(self, node: hulk_nodes.FunctionDeclarationNode, scope: Scope):
        function: Function = self.context.get_function(node.id)

        new_scope = scope.create_child()

        for i in range(len(function.param_names)):
            new_scope.define_variable(function.param_names[i], function.param_types[i])

        self.visit(node.expr, new_scope)

    @visitor.when(hulk_nodes.ExpressionBlockNode)
    def visit(self, node: hulk_nodes.ExpressionBlockNode, scope: Scope):
        expr_type = types.ErrorType()
        for expr in node.expressions:
            expr_type = self.visit(expr, scope)
        return expr_type

    @visitor.when(hulk_nodes.VarDeclarationNode)
    def visit(self, node: hulk_nodes.VarDeclarationNode, scope: Scope):
        # I don't want to include the var before to avoid let a = a in print(a);
        inf_type = self.visit(node.expr, scope)

        if node.var_type is not None:
            try:
                var_type = self.context.get_type_or_protocol(node.var_type)
            except SemanticError as e:
                self.errors.append(e)
                var_type = types.ErrorType()
        else:
            var_type = inf_type

        # todo look for covariance and contravariance (including protocols)
        if not inf_type.conforms_to(var_type):
            self.errors.append(SemanticError.INCOMPATIBLE_TYPES)
            var_type = types.ErrorType()

        scope.define_variable(node.id, var_type)

        return var_type

    @visitor.when(hulk_nodes.LetInNode)
    def visit(self, node: hulk_nodes.LetInNode, scope: Scope):
        # Create a new scope for every new variable declaration to allow redefining symbols
        old_scope = scope
        for declaration in node.var_declarations:
            new_scope = old_scope.create_child()
            self.visit(declaration, new_scope)
            old_scope = new_scope

        return self.visit(node.body, old_scope)

    @visitor.when(hulk_nodes.DestructiveAssignmentNode)
    def visit(self, node: hulk_nodes.DestructiveAssignmentNode, scope: Scope):
        new_type = self.visit(node.expr, scope)
        old_type = self.visit(node.target, scope)
        if not new_type.conforms_to(old_type):
            self.errors.append(SemanticError(SemanticError.INCOMPATIBLE_TYPES))
            return types.ErrorType()
        return old_type

    @visitor.when(hulk_nodes.ConditionalNode)
    def visit(self, node: hulk_nodes.ConditionalNode, scope: Scope):
        for condition in node.conditions:
            cond_type = self.visit(condition, scope.create_child())

            if not cond_type == types.BoolType():
                self.errors.append(SemanticError.INCOMPATIBLE_TYPES)
                # todo ??
                return types.ErrorType()

        lca_type = types.ErrorType()
        for expression in node.expressions:
            # todo lca
            self.visit(expression, scope.create_child())

        self.visit(node.default_expr, scope.create_child())

        return lca_type

    @visitor.when(hulk_nodes.WhileNode)
    def visit(self, node: hulk_nodes.WhileNode, scope: Scope):
        cond_type = self.visit(node.condition, scope.create_child())

        if cond_type != types.BoolType():
            self.errors.append(SemanticError.INCOMPATIBLE_TYPES)
            # todo ??
            return types.ErrorType()

        return self.visit(node.expression, scope.create_child())

    @visitor.when(hulk_nodes.FunctionCallNode)
    def visit(self, node: hulk_nodes.FunctionCallNode, scope: Scope):
        for arg in node.args:
            self.visit(arg, scope)

    @visitor.when(hulk_nodes.MethodCallNode)
    def visit(self, node: hulk_nodes.MethodCallNode, scope: Scope):
        for arg in node.args:
            self.visit(arg, scope)

    # todo for loop

    # todo vector initialization

    # todo false or error?
    @visitor.when(hulk_nodes.IsNode)
    def visit(self, node: hulk_nodes.IsNode, scope: Scope):
        expression_type = self.visit(node.expression, scope)

        try:
            cast_type = self.context.get_type(node.ttype)
        except SemanticError as e:
            self.errors.append(e)
            cast_type = types.ErrorType()

        if not expression_type.conforms_to(cast_type) and not cast_type.conforms_to(expression_type):
            return types.BoolType()

        return types.BoolType()

    @visitor.when(hulk_nodes.AsNode)
    def visit(self, node: hulk_nodes.AsNode, scope: Scope):
        expression_type = self.visit(node.expression, scope)
        try:
            cast_type = self.context.get_type(node.ttype)
        except SemanticError as e:
            self.errors.append(e)
            cast_type = types.ErrorType()

        if not expression_type.conforms_to(cast_type) and not cast_type.conforms_to(expression_type):
            self.errors.append(SemanticError.INCOMPATIBLE_TYPES)
            return types.ErrorType()
        return cast_type

    @visitor.when(hulk_nodes.ArithmeticExpressionNode)
    def visit(self, node: hulk_nodes.ArithmeticExpressionNode, scope: Scope):
        left_type = self.visit(node.left, scope)
        right_type = self.visit(node.right, scope)
        if not left_type == types.NumberType() or not right_type == types.NumberType():
            self.errors.append(SemanticError(SemanticError.INVALID_OPERATION))
            return types.ErrorType()
        return types.NumberType()

    @visitor.when(hulk_nodes.InequalityExpressionNode)
    def visit(self, node: hulk_nodes.ArithmeticExpressionNode, scope: Scope):
        left_type = self.visit(node.left, scope)
        right_type = self.visit(node.right, scope)
        if not left_type == types.NumberType() or not right_type == types.NumberType():
            self.errors.append(SemanticError(SemanticError.INVALID_OPERATION))
            return types.ErrorType()
        return types.BoolType()

    @visitor.when(hulk_nodes.BoolBinaryExpressionNode)
    def visit(self, node: hulk_nodes.BoolBinaryExpressionNode, scope: Scope):
        left_type = self.visit(node.left, scope)
        right_type = self.visit(node.right, scope)
        if not left_type == types.BoolType() or not right_type == types.BoolType():
            self.errors.append(SemanticError(SemanticError.INVALID_OPERATION))
            return types.ErrorType()
        return types.BoolType()

    # todo change is instance for a "has_implicit_cast" to accept print("The meaning of life is" @@ 42)
    @visitor.when(hulk_nodes.StrBinaryExpressionNode)
    def visit(self, node: hulk_nodes.StrBinaryExpressionNode, scope: Scope):
        left_type = self.visit(node.left, scope)
        right_type = self.visit(node.right, scope)
        if not left_type == types.StringType() or not right_type == types.StringType():
            self.errors.append(SemanticError(SemanticError.INVALID_OPERATION))
            return types.ErrorType()
        return types.StringType()

    # todo be more specific with True and False
    # todo l_type != r_type is error or false
    @visitor.when(hulk_nodes.EqualityExpressionNode)
    def visit(self, node: hulk_nodes.ArithmeticExpressionNode, scope: Scope):
        self.visit(node.left, scope)
        self.visit(node.right, scope)
        return types.BoolType()

    @visitor.when(hulk_nodes.NegNode)
    def visit(self, node: hulk_nodes.NegNode, scope: Scope):
        operand_type = self.visit(node.operand, scope)

        if operand_type == types.NumberType():
            self.errors.append(SemanticError(SemanticError.INCOMPATIBLE_TYPES))
            return types.NumberType()

        return types.BoolType()

    @visitor.when(hulk_nodes.NotNode)
    def visit(self, node: hulk_nodes.NotNode, scope: Scope):
        operand_type = self.visit(node.operand, scope)

        if operand_type == types.BoolType():
            self.errors.append(SemanticError(SemanticError.INCOMPATIBLE_TYPES))
            return types.ErrorType()

        return types.BoolType()

    @visitor.when(hulk_nodes.ConstantBoolNode)
    def visit(self, node: hulk_nodes.ConstantBoolNode, scope: Scope):
        return types.BoolType()

    @visitor.when(hulk_nodes.ConstantNumNode)
    def visit(self, node: hulk_nodes.ConstantNumNode, scope: Scope):
        return types.NumberType()

    @visitor.when(hulk_nodes.ConstantStringNode)
    def visit(self, node: hulk_nodes.ConstantStringNode, scope: Scope):
        return types.StringType()

    @visitor.when(hulk_nodes.VariableNode)
    def visit(self, node: hulk_nodes.VariableNode, scope: Scope):
        if not scope.is_defined(node.lex):
            self.errors.append(SemanticError(SemanticError.VARIABLE_NOT_DEFINED))
            return types.ErrorType()

        var = scope.find_variable(node.lex)
        return var.type

    @visitor.when(hulk_nodes.TypeInstantiationNode)
    def visit(self, node: hulk_nodes.TypeInstantiationNode, scope: Scope):
        try:
            ttype = self.context.get_type(node.idx)
        except SemanticError as e:
            self.errors.append(e)
            return types.ErrorType()

        args_types = [self.visit(arg, scope) for arg in node.args]

        # Check if the number of arguments is correct
        if len(args_types) != len(ttype.params_types):
            self.errors.append(SemanticError(
                f"Expected {len(ttype.params_types)} arguments, but {len(args_types)} were given."))
            return types.ErrorType()

        for i in range(len(args_types)):
            if not args_types[i].conforms_to(ttype.params_types[i]):
                self.errors.append(SemanticError(SemanticError.INCOMPATIBLE_TYPES))
                return types.ErrorType()

        return ttype
