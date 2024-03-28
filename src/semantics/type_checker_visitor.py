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
        self.current_function = None
        self.errors: list = errors

    def assign_auto_type(self, node, scope: Scope, other_type: (types.Type | types.Protocol)):
        # If I am assigning a type for a variable (or parameter), I will assign the most specialized type
        if isinstance(node, hulk_nodes.VariableNode):
            var_info = scope.find_variable(node.lex)
            var_info.type = types.get_most_specialized_type([other_type, var_info.type])
        # # If I am assigning a return type for a method or function, I will assign the lowest common ancestor
        # elif isinstance(node, hulk_nodes.FunctionCallNode):
        #     func = self.context.get_function(node.idx)
        #     func.return_type = types.get_lowest_common_ancestor([other_type, func.return_type])
        # elif isinstance(node, hulk_nodes.MethodCallNode):
        #     typex = self.visit(node.obj, scope)
        #     meth = typex.get_method(node.method)
        #     meth.return_type = types.get_lowest_common_ancestor([other_type, meth.return_type])

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

        params = zip(self.current_type.params_names, self.current_type.params_types)
        for param_name, param_type in params:
            new_scope.define_variable(param_name, param_type)

        for expr in node.parent_args:
            self.visit(expr, new_scope)

        for attr in node.attributes:
            attr_type = self.visit(attr, new_scope)
            attr = self.current_type.get_attribute(attr.id)
            attr.type = attr_type

        # Check if we could infer some params types
        for i in range(len(self.current_type.params_types)):
            if self.current_type.params_types[i] == types.AutoType():
                local_var = new_scope.find_variable(self.current_type.params_names[i])
                self.current_type.params_types[i] = local_var.type

        # Create a new scope that includes the self symbol
        methods_scope = scope.create_child()
        methods_scope.define_variable('self', self.current_type)
        for method in node.methods:
            self.visit(method, methods_scope)

    @visitor.when(hulk_nodes.AttributeDeclarationNode)
    def visit(self, node: hulk_nodes.AttributeDeclarationNode, scope: Scope):
        inf_type = self.visit(node.expr, scope)

        if node.attribute_type is not None:
            attr_type = self.context.get_type_or_protocol(node.attribute_type)
        else:
            attr_type = inf_type

        if not inf_type.conforms_to(attr_type):
            self.errors.append(SemanticError.INCOMPATIBLE_TYPES)
            attr_type = types.ErrorType()

        return attr_type

    @visitor.when(hulk_nodes.MethodDeclarationNode)
    def visit(self, node: hulk_nodes.MethodDeclarationNode, scope: Scope):
        method: Method = self.current_type.get_method(node.id)

        new_scope = scope.create_child()

        for i in range(len(method.param_names)):
            new_scope.define_variable(method.param_names[i], method.param_types[i])

        return_type = self.visit(node.expr, new_scope)

        # Check if we could infer some params types
        for i in range(len(method.param_types)):
            if method.param_types[i] == types.AutoType():
                local_var = new_scope.find_variable(method.param_names[i])
                method.param_types[i] = local_var.type

        return return_type

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
        cond_types = [self.visit(cond, scope.create_child()) for cond in node.conditions]

        for cond_type in cond_types:
            if cond_type != types.BoolType():
                self.errors.append(SemanticError.INCOMPATIBLE_TYPES)

        expr_types = [self.visit(expression, scope.create_child()) for expression in node.expressions]

        else_type = self.visit(node.default_expr, scope.create_child())

        return types.get_lowest_common_ancestor(expr_types + else_type)

    @visitor.when(hulk_nodes.WhileNode)
    def visit(self, node: hulk_nodes.WhileNode, scope: Scope):
        cond_type = self.visit(node.condition, scope.create_child())

        if cond_type != types.BoolType():
            self.errors.append(SemanticError.INCOMPATIBLE_TYPES)

        return self.visit(node.expression, scope.create_child())

    @visitor.when(hulk_nodes.FunctionCallNode)
    def visit(self, node: hulk_nodes.FunctionCallNode, scope: Scope):
        args_types = [self.visit(arg, scope) for arg in node.args]
        function = self.context.get_function(node.idx)

        if len(args_types) != len(function.param_types):
            self.errors.append(
                SemanticError(f"Expected {len(function.param_types)} arguments, but {len(args_types)} were given."))
            return types.ErrorType()

        for arg_type, param_type in zip(args_types, function.param_types):
            if not arg_type.conforms_to(param_type):
                self.errors.append(SemanticError.INCOMPATIBLE_TYPES)
                return types.ErrorType()

        return function.return_type

    @visitor.when(hulk_nodes.MethodCallNode)
    def visit(self, node: hulk_nodes.MethodCallNode, scope: Scope):
        args_types = [self.visit(arg, scope) for arg in node.args]
        method = self.current_type.get_method(node.method)

        if len(args_types) != len(method.param_types):
            self.errors.append(
                SemanticError(f"Expected {len(method.param_types)} arguments, but {len(args_types)} were given."))
            return types.ErrorType()

        for arg_type, param_type in zip(args_types, method.param_types):
            if not arg_type.conforms_to(param_type):
                self.errors.append(SemanticError.INCOMPATIBLE_TYPES)
                return types.ErrorType()

        return method.return_type

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
        if left_type == types.AutoType():
            self.assign_auto_type(node.left, scope, types.NumberType())
            left_type = types.NumberType()

        right_type = self.visit(node.right, scope)
        if right_type == types.AutoType():
            self.assign_auto_type(node.right, scope, types.NumberType())
            right_type = types.NumberType()

        if not left_type == types.NumberType() or not right_type == types.NumberType():
            self.errors.append(SemanticError(SemanticError.INVALID_OPERATION))
            return types.ErrorType()
        return types.NumberType()

    @visitor.when(hulk_nodes.InequalityExpressionNode)
    def visit(self, node: hulk_nodes.ArithmeticExpressionNode, scope: Scope):
        left_type = self.visit(node.left, scope)
        if left_type == types.AutoType():
            self.assign_auto_type(node.left, scope, types.NumberType())
            left_type = types.NumberType()

        right_type = self.visit(node.right, scope)
        if right_type == types.AutoType():
            self.assign_auto_type(node.right, scope, types.NumberType())
            right_type = types.NumberType()

        if not left_type == types.NumberType() or not right_type == types.NumberType():
            self.errors.append(SemanticError(SemanticError.INVALID_OPERATION))
            return types.ErrorType()

        return types.BoolType()

    @visitor.when(hulk_nodes.BoolBinaryExpressionNode)
    def visit(self, node: hulk_nodes.BoolBinaryExpressionNode, scope: Scope):
        left_type = self.visit(node.left, scope)
        if left_type == types.AutoType():
            self.assign_auto_type(node.left, scope, types.BoolType())
            left_type = types.BoolType()

        right_type = self.visit(node.right, scope)
        if right_type == types.AutoType():
            self.assign_auto_type(node.right, scope, types.BoolType())
            right_type = types.BoolType()

        if not left_type == types.BoolType() or not right_type == types.BoolType():
            self.errors.append(SemanticError(SemanticError.INVALID_OPERATION))
            return types.ErrorType()
        return types.BoolType()

    # todo change is instance for a "has_implicit_cast" to accept print("The meaning of life is" @@ 42)
    @visitor.when(hulk_nodes.StrBinaryExpressionNode)
    def visit(self, node: hulk_nodes.StrBinaryExpressionNode, scope: Scope):
        left_type = self.visit(node.left, scope)
        right_type = self.visit(node.right, scope)

        # todo
        # left_type = self.visit(node.left, scope)
        # if left_type == types.AutoType():
        #     self.assign_auto_type(node.left, scope, types.StringType())
        #     left_type = types.StringType()
        #
        # right_type = self.visit(node.right, scope)
        # if right_type == types.AutoType():
        #     self.assign_auto_type(node.right, scope, types.StringType())
        #     right_type = types.StringType()

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

        if operand_type == types.AutoType():
            self.assign_auto_type(node.operand, scope, types.NumberType())
            operand_type = types.NumberType()

        if operand_type == types.NumberType():
            self.errors.append(SemanticError(SemanticError.INCOMPATIBLE_TYPES))
            return types.NumberType()

        return types.BoolType()

    @visitor.when(hulk_nodes.NotNode)
    def visit(self, node: hulk_nodes.NotNode, scope: Scope):
        operand_type = self.visit(node.operand, scope)

        if operand_type == types.AutoType():
            self.assign_auto_type(node.operand, scope, types.BoolType())
            operand_type = types.BoolType()

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

        for arg_type, param_type in zip(args_types, ttype.params_types):
            if not arg_type.conforms_to(param_type):
                self.errors.append(SemanticError(SemanticError.INCOMPATIBLE_TYPES))
                return types.ErrorType()

        return ttype
