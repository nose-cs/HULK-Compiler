from typing import List

import src.hulk_grammar.hulk_ast_nodes as hulk_nodes
import src.semantics.types as types
import src.visitor as visitor
from src.errors import SemanticError
from src.semantics.types import Method
from src.semantics.utils import Scope, Context, Function


class TypeInfer(object):
    def __init__(self, context, errors=None) -> None:
        if errors is None:
            errors = []
        self.context: Context = context
        self.current_type = None
        self.errors: List[SemanticError] = errors

    @staticmethod
    def assign_auto_type(node, scope: Scope, other_type: (types.Type | types.Protocol)):
        """
        Add the inferred type to the variable in the scope
        :param node: The node that was inferred
        :param scope: The scope where the variable is
        :param other_type: The inferred type
        :return: None
        """
        if other_type == types.AutoType():
            return
        if isinstance(node, hulk_nodes.VariableNode):
            var_info = scope.find_variable(node.lex)
            var_info.inferred_types.append(other_type)

    @visitor.on('node')
    def visit(self, node, scope):
        pass

    @visitor.when(hulk_nodes.ProgramNode)
    def visit(self, node: hulk_nodes.ProgramNode, scope: Scope):
        for declaration, child_scope in zip(node.declarations, scope.children):
            self.visit(declaration, child_scope)

        self.visit(node.expression, scope.children[-1])

        return scope

    @visitor.when(hulk_nodes.TypeDeclarationNode)
    def visit(self, node: hulk_nodes.TypeDeclarationNode, scope: Scope):
        self.current_type = self.context.get_type(node.idx)

        new_scope = scope.children[0]

        for expr in node.parent_args:
            self.visit(expr, new_scope)

        for attr in node.attributes:
            attr_type = self.visit(attr, new_scope)
            attribute = self.current_type.get_attribute(attr.id)
            if attribute.type == types.AutoType():
                if attr_type == types.AutoType():
                    self.errors.append(SemanticError("Cannot infer the type of the attribute, please specify it."))
                    attr_type = types.ErrorType()
                attribute.type = attr_type

        # Check if we could infer some params types
        for i in range(len(self.current_type.params_types)):
            if self.current_type.params_types[i] == types.AutoType():
                local_var = new_scope.find_variable(self.current_type.params_names[i])
                if local_var.inferred_types:
                    new_type = types.get_most_specialized_type(local_var.inferred_types)
                    self.current_type.params_types[i] = new_type
                    local_var.type = new_type
                    if new_type.is_error():
                        self.errors.append(SemanticError(SemanticError.INCONSISTENT_USE))
                else:
                    self.errors.append(SemanticError("Cannot infer the type of the param, please specify it."))
                    local_var.type = types.ErrorType()

        # Infer the params types and return type of the methods
        methods_scope = scope.children[1]
        for method in node.methods:
            self.visit(method, methods_scope)

    @visitor.when(hulk_nodes.AttributeDeclarationNode)
    def visit(self, node: hulk_nodes.AttributeDeclarationNode, scope: Scope):
        inf_type = self.visit(node.expr, scope)

        if node.attribute_type is not None:
            attr_type = self.context.get_type_or_protocol(node.attribute_type)
        else:
            attr_type = inf_type

        return attr_type

    @visitor.when(hulk_nodes.MethodDeclarationNode)
    def visit(self, node: hulk_nodes.MethodDeclarationNode, scope: Scope):
        method: Method = self.current_type.get_method(node.id)

        method_scope = scope.children[0]
        return_type = self.visit(node.expr, method_scope)

        if method.return_type == types.AutoType():
            method.return_type = return_type

        # Check if we could infer some params types
        for i in range(len(method.param_types)):
            if method.param_types[i] == types.AutoType():
                local_var = method_scope.find_variable(method.param_names[i])
                if local_var.inferred_types:
                    new_type = types.get_most_specialized_type(local_var.inferred_types)
                    method.param_types[i] = new_type
                    local_var.type = new_type
                    if new_type.is_error():
                        self.errors.append(SemanticError(SemanticError.INCONSISTENT_USE))
                else:
                    self.errors.append(SemanticError("Cannot infer the type of the param, please specify it."))
                    local_var.type = types.ErrorType()

        return return_type

    @visitor.when(hulk_nodes.FunctionDeclarationNode)
    def visit(self, node: hulk_nodes.FunctionDeclarationNode, scope: Scope):
        function: Function = self.context.get_function(node.id)

        new_scope = scope.children[0]
        return_type = self.visit(node.expr, new_scope)

        if function.return_type == types.AutoType():
            function.return_type = return_type

        # Check if we could infer some params types
        for i in range(len(function.param_types)):
            if function.param_types[i] == types.AutoType():
                local_var = new_scope.find_variable(function.param_names[i])
                if local_var.inferred_types:
                    new_type = types.get_most_specialized_type(local_var.inferred_types)
                    function.param_types[i] = new_type
                    local_var.type = new_type
                    if new_type.is_error():
                        self.errors.append(SemanticError(SemanticError.INCONSISTENT_USE))
                else:
                    self.errors.append(SemanticError("Cannot infer the type of the param, please specify it."))
                    local_var.type = types.ErrorType()

        return return_type

    @visitor.when(hulk_nodes.ExpressionBlockNode)
    def visit(self, node: hulk_nodes.ExpressionBlockNode, scope: Scope):
        block_scope = scope.children[0]
        expr_type = types.ErrorType()
        for expr in node.expressions:
            expr_type = self.visit(expr, block_scope)
        return expr_type

    @visitor.when(hulk_nodes.VarDeclarationNode)
    def visit(self, node: hulk_nodes.VarDeclarationNode, scope: Scope):
        # I don't want to include the var before to avoid let a = a in print(a);
        inf_type = self.visit(node.expr, scope)

        var = scope.find_variable(node.id)
        var.type = var.type if var.type != types.AutoType() else inf_type

        return var.type

    @visitor.when(hulk_nodes.LetInNode)
    def visit(self, node: hulk_nodes.LetInNode, scope: Scope):
        let_in_scope = scope

        for declaration in node.var_declarations:
            var_scope = let_in_scope.children[0]
            self.visit(declaration, var_scope)
            let_in_scope = var_scope

        return_type = self.visit(node.body, let_in_scope)

        return return_type

    @visitor.when(hulk_nodes.DestructiveAssignmentNode)
    def visit(self, node: hulk_nodes.DestructiveAssignmentNode, scope: Scope):
        self.visit(node.expr, scope)
        old_type = self.visit(node.target, scope)
        return old_type

    @visitor.when(hulk_nodes.ConditionalNode)
    def visit(self, node: hulk_nodes.ConditionalNode, scope: Scope):
        cond_types = [self.visit(cond, child_scope) for cond, child_scope in zip(node.conditions, scope.children)]

        expr_types = [self.visit(expression, child_scope) for expression, child_scope in
                      zip(node.expressions, scope.children[len(cond_types):])]

        else_type = self.visit(node.default_expr, scope.children[-1])

        return types.get_lowest_common_ancestor(expr_types + [else_type])

    @visitor.when(hulk_nodes.WhileNode)
    def visit(self, node: hulk_nodes.WhileNode, scope: Scope):
        self.visit(node.condition, scope.children[0])
        return self.visit(node.expression, scope.children[1])

    @visitor.when(hulk_nodes.FunctionCallNode)
    def visit(self, node: hulk_nodes.FunctionCallNode, scope: Scope):
        try:
            function = self.context.get_function(node.idx)

            for arg, param_type in zip(node.args, function.param_types):
                self.visit(arg, scope)
                self.assign_auto_type(arg, scope, param_type)

            return function.return_type
        except SemanticError as e:
            self.errors.append(e)
            return types.ErrorType()

    @visitor.when(hulk_nodes.MethodCallNode)
    def visit(self, node: hulk_nodes.MethodCallNode, scope: Scope):
        if not scope.is_defined(node.obj):
            obj_type = self.visit(node.obj, scope)
        else:
            obj_type = scope.find_variable(node.obj).type

        try:
            method = self.current_type.get_method(node.method) if obj_type == types.SelfType() else obj_type.get_method(
                node.method)
            for arg, param_type in zip(node.args, method.param_types):
                self.visit(arg, scope)
                self.assign_auto_type(arg, scope, param_type)
            return method.return_type
        except SemanticError as e:
            self.errors.append(e)
            return types.ErrorType()

    @visitor.when(hulk_nodes.AttributeCallNode)
    def visit(self, node: hulk_nodes.AttributeCallNode, scope: Scope):
        if not scope.is_defined(node.obj):
            obj_type = self.visit(node.obj, scope)
        else:
            obj_type = scope.find_variable(node.obj).type

        if obj_type == types.SelfType():
            try:
                attr = self.current_type.get_attribute(node.attribute)
                return attr.type
            except SemanticError as e:
                self.errors.append(e)
                return types.ErrorType()
        else:
            self.errors.append(SemanticError("Cannot access an attribute from a non-self object"))
            return types.ErrorType()

    # todo for loop

    # todo vector initialization

    # todo false or error?
    @visitor.when(hulk_nodes.IsNode)
    def visit(self, node: hulk_nodes.IsNode, scope: Scope):
        bool_type = self.context.get_type('Bool')
        self.visit(node.expression, scope)
        return bool_type

    @visitor.when(hulk_nodes.AsNode)
    def visit(self, node: hulk_nodes.AsNode, scope: Scope):
        self.visit(node.expression, scope)
        cast_type = self.context.get_type(node.ttype)
        return cast_type

    @visitor.when(hulk_nodes.ArithmeticExpressionNode)
    def visit(self, node: hulk_nodes.ArithmeticExpressionNode, scope: Scope):
        number_type = self.context.get_type('Number')

        left_type = self.visit(node.left, scope)
        if left_type == types.AutoType():
            self.assign_auto_type(node.left, scope, number_type)

        right_type = self.visit(node.right, scope)
        if right_type == types.AutoType():
            self.assign_auto_type(node.right, scope, number_type)

        return number_type

    @visitor.when(hulk_nodes.InequalityExpressionNode)
    def visit(self, node: hulk_nodes.ArithmeticExpressionNode, scope: Scope):
        bool_type = self.context.get_type('Bool')
        number_type = self.context.get_type('Number')

        left_type = self.visit(node.left, scope)
        if left_type == types.AutoType():
            self.assign_auto_type(node.left, scope, number_type)

        right_type = self.visit(node.right, scope)
        if right_type == types.AutoType():
            self.assign_auto_type(node.right, scope, number_type)

        return bool_type

    @visitor.when(hulk_nodes.BoolBinaryExpressionNode)
    def visit(self, node: hulk_nodes.BoolBinaryExpressionNode, scope: Scope):
        bool_type = self.context.get_type('Bool')

        left_type = self.visit(node.left, scope)
        if left_type == types.AutoType():
            self.assign_auto_type(node.left, scope, bool_type)

        right_type = self.visit(node.right, scope)
        if right_type == types.AutoType():
            self.assign_auto_type(node.right, scope, bool_type)

        return bool_type

    # todo change is instance for a "has_implicit_cast" to accept print("The meaning of life is" @@ 42)
    @visitor.when(hulk_nodes.StrBinaryExpressionNode)
    def visit(self, node: hulk_nodes.StrBinaryExpressionNode, scope: Scope):
        string_type = self.context.get_type('Number')
        object_type = self.context.get_type('Object')

        left_type = self.visit(node.left, scope)
        if left_type == types.AutoType():
            self.assign_auto_type(node.left, scope, object_type)

        right_type = self.visit(node.right, scope)
        if right_type == types.AutoType():
            self.assign_auto_type(node.right, scope, object_type)

        return string_type

    # todo be more specific with True and False
    # todo l_type != r_type is error or false
    @visitor.when(hulk_nodes.EqualityExpressionNode)
    def visit(self, node: hulk_nodes.ArithmeticExpressionNode, scope: Scope):
        self.visit(node.left, scope)
        self.visit(node.right, scope)
        return self.context.get_type('Bool')

    @visitor.when(hulk_nodes.NegNode)
    def visit(self, node: hulk_nodes.NegNode, scope: Scope):
        operand_type = self.visit(node.operand, scope)
        number_type = self.context.get_type('Number')

        if operand_type == types.AutoType():
            self.assign_auto_type(node.operand, scope, number_type)

        return number_type

    @visitor.when(hulk_nodes.NotNode)
    def visit(self, node: hulk_nodes.NotNode, scope: Scope):
        operand_type = self.visit(node.operand, scope)
        bool_type = self.context.get_type('Bool')

        if operand_type == types.AutoType():
            self.assign_auto_type(node.operand, scope, bool_type)

        return bool_type

    @visitor.when(hulk_nodes.ConstantBoolNode)
    def visit(self, node: hulk_nodes.ConstantBoolNode, scope: Scope):
        return self.context.get_type('Bool')

    @visitor.when(hulk_nodes.ConstantNumNode)
    def visit(self, node: hulk_nodes.ConstantNumNode, scope: Scope):
        return self.context.get_type('Number')

    @visitor.when(hulk_nodes.ConstantStringNode)
    def visit(self, node: hulk_nodes.ConstantStringNode, scope: Scope):
        return self.context.get_type('String')

    @visitor.when(hulk_nodes.VariableNode)
    def visit(self, node: hulk_nodes.VariableNode, scope: Scope):
        var = scope.find_variable(node.lex)
        return var.type

    @visitor.when(hulk_nodes.TypeInstantiationNode)
    def visit(self, node: hulk_nodes.TypeInstantiationNode, scope: Scope):
        ttype = self.context.get_type(node.idx)
        return ttype
