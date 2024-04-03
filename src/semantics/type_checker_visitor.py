from typing import List

import src.hulk_grammar.hulk_ast_nodes as hulk_nodes
import src.semantics.types as types
import src.visitor as visitor
from src.errors import SemanticError
from src.semantics.utils import Scope, Context, Function


class TypeChecker(object):
    def __init__(self, context, errors=None) -> None:
        if errors is None:
            errors = []
        self.context: Context = context
        self.current_type = None
        self.current_method = None
        self.errors: List[SemanticError] = errors

    @visitor.on('node')
    def visit(self, node: hulk_nodes.Node, scope: Scope):
        pass

    @visitor.when(hulk_nodes.ProgramNode)
    def visit(self, node: hulk_nodes.ProgramNode, scope: Scope = None):
        for declaration, child_scope in zip(node.declarations, scope.children):
            self.visit(declaration, child_scope)

        self.visit(node.expression, scope.children[-1])

        return scope

    @visitor.when(hulk_nodes.TypeDeclarationNode)
    def visit(self, node: hulk_nodes.TypeDeclarationNode, scope: Scope):
        self.current_type = self.context.get_type(node.idx)

        new_scope = scope.children[0]

        for attr in node.attributes:
            self.visit(attr, new_scope)

        methods_scope = scope.children[1]
        for method in node.methods:
            self.visit(method, methods_scope)

        if isinstance(self.current_type.parent, types.ErrorType):
            return

        parent_args_types = [self.visit(expr, new_scope) for expr in node.parent_args]

        parent_params_types = self.current_type.parent.params_types

        if len(parent_args_types) != len(parent_params_types):
            error_text = SemanticError.EXPECTED_ARGUMENTS % (
                len(parent_params_types), len(parent_args_types), self.current_type.parent.name)
            self.errors.append(SemanticError(error_text))
            return types.ErrorType()

        for parent_arg_type, parent_param_type in zip(parent_args_types, parent_params_types):
            if not parent_arg_type.conforms_to(parent_param_type):
                error_text = SemanticError.INCOMPATIBLE_TYPES % (parent_arg_type.name, parent_param_type.name)
                self.errors.append(SemanticError(error_text))

        self.current_type = None

    @visitor.when(hulk_nodes.AttributeDeclarationNode)
    def visit(self, node: hulk_nodes.AttributeDeclarationNode, scope: Scope):
        inf_type = self.visit(node.expr, scope)

        attr_type = self.current_type.get_attribute(node.id).type

        if not inf_type.conforms_to(attr_type):
            error_text = SemanticError.INCOMPATIBLE_TYPES % (inf_type.name, attr_type.name)
            self.errors.append(SemanticError(error_text))

        return attr_type

    @visitor.when(hulk_nodes.MethodDeclarationNode)
    def visit(self, node: hulk_nodes.MethodDeclarationNode, scope: Scope):
        self.current_method = self.current_type.get_method(node.id)

        new_scope = scope.children[0]

        return_type = self.visit(node.expr, new_scope)

        if self.current_type.parent is None:
            return return_type

        # Check if override is correct
        try:
            parent_method = self.current_type.parent.get_method(node.id)
        except SemanticError:
            parent_method = None

        if parent_method is None:
            return return_type

        error_text = SemanticError.WRONG_SIGNATURE % parent_method
        if parent_method.return_type != return_type:
            self.errors.append(SemanticError(error_text))
            return_type = types.ErrorType()
        if len(parent_method.param_types) != len(self.current_method.param_types):
            self.errors.append(SemanticError(error_text))
            return_type = types.ErrorType()

        for i in range(len(parent_method.param_types)):
            if parent_method.param_types[i] != self.current_method.param_types[i]:
                self.errors.append(SemanticError(error_text))
                self.current_method.param_types[i] = types.ErrorType()
                return_type = types.ErrorType()

        self.current_method = None

        return return_type

    @visitor.when(hulk_nodes.FunctionDeclarationNode)
    def visit(self, node: hulk_nodes.FunctionDeclarationNode, scope: Scope):
        function: Function = self.context.get_function(node.id)

        new_scope = scope.children[0]

        inf_return_type = self.visit(node.expr, new_scope)

        if not inf_return_type.conforms_to(function.return_type):
            error_text = SemanticError.INCOMPATIBLE_TYPES % (inf_return_type.name, function.return_type.name)
            self.errors.append(SemanticError(error_text))
            return types.ErrorType()

        return function.return_type

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
        var_type = scope.find_variable(node.id).type

        if not inf_type.conforms_to(var_type):
            error_text = SemanticError.INCOMPATIBLE_TYPES % (inf_type.name, var_type.name)
            self.errors.append(SemanticError(error_text))
            var_type = types.ErrorType()

        return var_type

    @visitor.when(hulk_nodes.LetInNode)
    def visit(self, node: hulk_nodes.LetInNode, scope: Scope):
        old_scope = scope

        for declaration in node.var_declarations:
            new_scope = old_scope.children[0]
            self.visit(declaration, new_scope)
            old_scope = new_scope

        return self.visit(node.body, old_scope)

    @visitor.when(hulk_nodes.DestructiveAssignmentNode)
    def visit(self, node: hulk_nodes.DestructiveAssignmentNode, scope: Scope):
        new_type = self.visit(node.expr, scope)
        old_type = self.visit(node.target, scope)

        if old_type.name == 'Self':
            self.errors.append(SemanticError(SemanticError.SELF_IS_READONLY))
            return types.ErrorType()

        if not new_type.conforms_to(old_type):
            error_text = SemanticError.INCOMPATIBLE_TYPES % (new_type.name, old_type.name)
            self.errors.append(SemanticError(error_text))
            return types.ErrorType()

        return old_type

    @visitor.when(hulk_nodes.ConditionalNode)
    def visit(self, node: hulk_nodes.ConditionalNode, scope: Scope):
        cond_types = [self.visit(cond, child_scope) for cond, child_scope in zip(node.conditions, scope.children)]

        for cond_type in cond_types:
            if cond_type != types.BoolType():
                error_text = SemanticError.INCOMPATIBLE_TYPES % (cond_type.name, types.BoolType().name)
                self.errors.append(SemanticError(error_text))

        expr_types = [self.visit(expression, child_scope) for expression, child_scope in
                      zip(node.expressions, scope.children[len(cond_types):])]

        else_type = self.visit(node.default_expr, scope.children[-1])

        return types.get_lowest_common_ancestor(expr_types + [else_type])

    @visitor.when(hulk_nodes.WhileNode)
    def visit(self, node: hulk_nodes.WhileNode, scope: Scope):
        cond_type = self.visit(node.condition, scope.children[0])

        if cond_type != types.BoolType():
            error_text = SemanticError.INCOMPATIBLE_TYPES % (cond_type.name, types.BoolType().name)
            self.errors.append(SemanticError(error_text))

        return self.visit(node.expression, scope.children[1])

    @visitor.when(hulk_nodes.ForNode)
    def visit(self, node: hulk_nodes.ForNode, scope: Scope):
        ttype = self.visit(node.iterable, scope.children[1])
        iterable_protocol = self.context.get_protocol('Iterable')

        if not ttype.conforms_to(iterable_protocol):
            error_text = SemanticError.INCOMPATIBLE_TYPES % (ttype.name, iterable_protocol.name)
            self.errors.append(SemanticError(error_text))

        return self.visit(node.expression, scope.children[0])

    @visitor.when(hulk_nodes.FunctionCallNode)
    def visit(self, node: hulk_nodes.FunctionCallNode, scope: Scope):
        args_types = [self.visit(arg, scope) for arg in node.args]

        try:
            function = self.context.get_function(node.idx)
        except SemanticError as e:
            self.errors.append(e)
            return types.ErrorType()

        if len(args_types) != len(function.param_types):
            error_text = SemanticError.EXPECTED_ARGUMENTS % (len(function.param_types), len(args_types), function.name)
            self.errors.append(SemanticError(error_text))
            return types.ErrorType()

        for arg_type, param_type in zip(args_types, function.param_types):
            if not arg_type.conforms_to(param_type):
                error_text = SemanticError.INCOMPATIBLE_TYPES % (arg_type.name, param_type.name)
                self.errors.append(SemanticError(error_text))
                return types.ErrorType()

        return function.return_type

    @visitor.when(hulk_nodes.MethodCallNode)
    def visit(self, node: hulk_nodes.MethodCallNode, scope: Scope):
        args_types = [self.visit(arg, scope) for arg in node.args]

        if not scope.is_defined(node.obj):
            obj_type = self.visit(node.obj, scope)
        else:
            obj_type = scope.find_variable(node.obj).type

        if isinstance(obj_type, types.ErrorType):
            return types.ErrorType()

        try:
            if obj_type == types.SelfType():
                method = self.current_type.get_method(node.method)
            else:
                method = obj_type.get_method(node.method)
        except SemanticError as e:
            self.errors.append(e)
            return types.ErrorType()

        if len(args_types) != len(method.param_types):
            error_text = SemanticError.EXPECTED_ARGUMENTS % (len(method.param_types), len(args_types), method.name)
            self.errors.append(SemanticError(error_text))
            return types.ErrorType()

        for arg_type, param_type in zip(args_types, method.param_types):
            if not arg_type.conforms_to(param_type):
                error_text = SemanticError.INCOMPATIBLE_TYPES % (arg_type.name, param_type.name)
                self.errors.append(SemanticError(error_text))
                return types.ErrorType()

        return method.return_type

    @visitor.when(hulk_nodes.BaseCallNode)
    def visit(self, node: hulk_nodes.BaseCallNode, scope: Scope):
        if self.current_method is None:
            self.errors.append(SemanticError(SemanticError.BASE_OUTSIDE_METHOD))
            return types.ErrorType()

        try:
            method = self.current_type.parent.get_method(self.current_method.name)
        except SemanticError:
            error_text = SemanticError.METHOD_NOT_DEFINED % self.current_method.name
            self.errors.append(SemanticError(error_text))
            return types.ErrorType()

        args_types = [self.visit(arg, scope) for arg in node.args]

        if len(args_types) != len(method.param_types):
            error_text = SemanticError.EXPECTED_ARGUMENTS % (len(method.param_types), len(args_types), method.name)
            self.errors.append(SemanticError(error_text))
            return types.ErrorType()

        for arg_type, param_type in zip(args_types, method.param_types):
            if not arg_type.conforms_to(param_type):
                error_text = SemanticError.INCOMPATIBLE_TYPES % (arg_type.name, param_type.name)
                self.errors.append(SemanticError(error_text))
                return types.ErrorType()

        return method.return_type

    @visitor.when(hulk_nodes.AttributeCallNode)
    def visit(self, node: hulk_nodes.AttributeCallNode, scope: Scope):
        if not scope.is_defined(node.obj):
            obj_type = self.visit(node.obj, scope)
        else:
            obj_type = scope.find_variable(node.obj).type

        if isinstance(obj_type, types.ErrorType):
            return types.ErrorType()

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

    @visitor.when(hulk_nodes.IsNode)
    def visit(self, node: hulk_nodes.IsNode, scope: Scope):
        self.visit(node.expression, scope)
        bool_type = self.context.get_type('Boolean')
        self.context.get_type_or_protocol(node.ttype)
        return bool_type

    @visitor.when(hulk_nodes.AsNode)
    def visit(self, node: hulk_nodes.AsNode, scope: Scope):
        expression_type = self.visit(node.expression, scope)

        cast_type = self.context.get_type_or_protocol(node.ttype)

        if not expression_type.conforms_to(cast_type) and not cast_type.conforms_to(expression_type):
            error_text = SemanticError.INCOMPATIBLE_TYPES % (expression_type.name, cast_type.name)
            self.errors.append(SemanticError(error_text))
            return types.ErrorType()

        return cast_type

    @visitor.when(hulk_nodes.ArithmeticExpressionNode)
    def visit(self, node: hulk_nodes.ArithmeticExpressionNode, scope: Scope):
        number_type = self.context.get_type('Number')

        left_type = self.visit(node.left, scope)

        right_type = self.visit(node.right, scope)

        if not left_type == types.NumberType() or not right_type == types.NumberType():
            error_text = SemanticError.INVALID_OPERATION % (node.operator, left_type.name, right_type.name)
            self.errors.append(SemanticError(error_text))
            return types.ErrorType()

        return number_type

    @visitor.when(hulk_nodes.InequalityExpressionNode)
    def visit(self, node: hulk_nodes.ArithmeticExpressionNode, scope: Scope):
        bool_type = self.context.get_type('Boolean')

        left_type = self.visit(node.left, scope)

        right_type = self.visit(node.right, scope)

        if not left_type == types.NumberType() or not right_type == types.NumberType():
            error_text = SemanticError.INVALID_OPERATION % (node.operator, left_type.name, right_type.name)
            self.errors.append(SemanticError(error_text))
            return types.ErrorType()

        return bool_type

    @visitor.when(hulk_nodes.BoolBinaryExpressionNode)
    def visit(self, node: hulk_nodes.BoolBinaryExpressionNode, scope: Scope):
        bool_type = self.context.get_type('Boolean')

        left_type = self.visit(node.left, scope)

        right_type = self.visit(node.right, scope)

        if not left_type == types.BoolType() or not right_type == types.BoolType():
            error_text = SemanticError.INVALID_OPERATION % (node.operator, left_type.name, right_type.name)
            self.errors.append(SemanticError(error_text))
            return types.ErrorType()

        return bool_type

    @visitor.when(hulk_nodes.StrBinaryExpressionNode)
    def visit(self, node: hulk_nodes.StrBinaryExpressionNode, scope: Scope):
        string_type = self.context.get_type('String')
        object_type = self.context.get_type('Object')

        left_type = self.visit(node.left, scope)

        right_type = self.visit(node.right, scope)

        if not left_type.conforms_to(object_type) or not right_type.conforms_to(object_type):
            error_text = SemanticError.INVALID_OPERATION % (node.operator, left_type.name, right_type.name)
            self.errors.append(SemanticError(error_text))
            return types.ErrorType()

        return string_type

    @visitor.when(hulk_nodes.EqualityExpressionNode)
    def visit(self, node: hulk_nodes.ArithmeticExpressionNode, scope: Scope):
        left_type = self.visit(node.left, scope)
        right_type = self.visit(node.right, scope)

        if not left_type.conforms_to(right_type) and not right_type.conforms_to(left_type):
            error_text = SemanticError.INVALID_OPERATION % (node.operator, left_type.name, right_type.name)
            self.errors.append(SemanticError(error_text))
            return types.ErrorType()

        return self.context.get_type('Boolean')

    @visitor.when(hulk_nodes.NegNode)
    def visit(self, node: hulk_nodes.NegNode, scope: Scope):
        operand_type = self.visit(node.operand, scope)
        number_type = self.context.get_type('Number')

        if operand_type != types.NumberType():
            error_text = SemanticError.INVALID_UNARY_OPERATION % (node.operator, operand_type.name)
            self.errors.append(SemanticError(error_text))
            return number_type

        return number_type

    @visitor.when(hulk_nodes.NotNode)
    def visit(self, node: hulk_nodes.NotNode, scope: Scope):
        operand_type = self.visit(node.operand, scope)
        bool_type = self.context.get_type('Boolean')

        if operand_type != types.BoolType():
            error_text = SemanticError.INVALID_UNARY_OPERATION % (node.operator, operand_type.name)
            self.errors.append(SemanticError(error_text))
            return types.ErrorType()

        return bool_type

    @visitor.when(hulk_nodes.ConstantBoolNode)
    def visit(self, node: hulk_nodes.ConstantBoolNode, scope: Scope):
        return self.context.get_type('Boolean')

    @visitor.when(hulk_nodes.ConstantNumNode)
    def visit(self, node: hulk_nodes.ConstantNumNode, scope: Scope):
        return self.context.get_type('Number')

    @visitor.when(hulk_nodes.ConstantStringNode)
    def visit(self, node: hulk_nodes.ConstantStringNode, scope: Scope):
        return self.context.get_type('String')

    @visitor.when(hulk_nodes.VariableNode)
    def visit(self, node: hulk_nodes.VariableNode, scope: Scope):
        if not scope.is_defined(node.lex):
            error_text = SemanticError.VARIABLE_NOT_DEFINED % node.lex
            self.errors.append(SemanticError(error_text))
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

        if len(args_types) != len(ttype.params_types):
            error_text = SemanticError.EXPECTED_ARGUMENTS % (len(ttype.params_types), len(args_types), ttype.name)
            self.errors.append(SemanticError(error_text))
            return types.ErrorType()

        for arg_type, param_type in zip(args_types, ttype.params_types):
            if not arg_type.conforms_to(param_type):
                error_text = SemanticError.INCOMPATIBLE_TYPES % (arg_type.name, param_type.name)
                self.errors.append(SemanticError(error_text))
                return types.ErrorType()

        return ttype

    @visitor.when(hulk_nodes.VectorInitializationNode)
    def visit(self, node: hulk_nodes.VectorInitializationNode, scope: Scope):
        elements_types = [self.visit(element, scope) for element in node.elements]
        lca = types.get_lowest_common_ancestor(elements_types)
        return types.VectorType(lca)

    @visitor.when(hulk_nodes.VectorComprehensionNode)
    def visit(self, node: hulk_nodes.VectorComprehensionNode, scope: Scope):
        ttype = self.visit(node.iterable, scope.children[0])
        iterable_protocol = self.context.get_protocol('Iterable')

        if not ttype.conforms_to(iterable_protocol):
            error_text = SemanticError.INCOMPATIBLE_TYPES % (ttype.name, iterable_protocol.name)
            self.errors.append(SemanticError(error_text))
            return types.ErrorType()

        return self.visit(node.selector, scope.children[0])

    @visitor.when(hulk_nodes.IndexingNode)
    def visit(self, node: hulk_nodes.IndexingNode, scope: Scope):
        number_type = self.context.get_type('Number')

        index_type = self.visit(node.index, scope)
        if index_type != number_type:
            error_text = SemanticError.INCOMPATIBLE_TYPES % (index_type.name, number_type.name)
            self.errors.append(SemanticError(error_text))
            return types.ErrorType()

        obj_type = self.visit(node.obj, scope)

        if obj_type.is_error():
            return types.ErrorType()

        if not isinstance(obj_type, types.VectorType):
            error_text = SemanticError.INVALID_UNARY_OPERATION % ('[]', obj_type.name)
            self.errors.append(SemanticError(error_text))
            return types.ErrorType()

        return obj_type.get_element_type()
