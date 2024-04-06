from typing import List

import src.hulk_grammar.hulk_ast_nodes as hulk_nodes
import src.semantics.types as types
import src.visitor as visitor
from src.errors import HulkSemanticError
from src.semantics.utils import Context, Function


class TypeChecker(object):
    def __init__(self, context, errors=None) -> None:
        if errors is None:
            errors = []
        self.context: Context = context
        self.current_type = None
        self.current_method = None
        self.errors: List[HulkSemanticError] = errors

    @visitor.on('node')
    def visit(self, node: hulk_nodes.Node):
        pass

    @visitor.when(hulk_nodes.ProgramNode)
    def visit(self, node: hulk_nodes.ProgramNode):
        for declaration in node.declarations:
            self.visit(declaration)

        self.visit(node.expression)

    @visitor.when(hulk_nodes.TypeDeclarationNode)
    def visit(self, node: hulk_nodes.TypeDeclarationNode):
        self.current_type = self.context.get_type(node.idx)

        for attr in node.attributes:
            self.visit(attr)

        for method in node.methods:
            self.visit(method)

        if isinstance(self.current_type.parent, types.ErrorType):
            return

        parent_args_types = [self.visit(expr) for expr in node.parent_args]

        parent_params_types = self.current_type.parent.params_types

        if len(parent_args_types) != len(parent_params_types):
            error_text = HulkSemanticError.EXPECTED_ARGUMENTS % (
                len(parent_params_types), len(parent_args_types), self.current_type.parent.name)
            self.errors.append(HulkSemanticError(error_text))
            return types.ErrorType()

        for parent_arg_type, parent_param_type in zip(parent_args_types, parent_params_types):
            if not parent_arg_type.conforms_to(parent_param_type):
                error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (parent_arg_type.name, parent_param_type.name)
                self.errors.append(HulkSemanticError(error_text))

        self.current_type = None

    @visitor.when(hulk_nodes.AttributeDeclarationNode)
    def visit(self, node: hulk_nodes.AttributeDeclarationNode):
        inf_type = self.visit(node.expr)

        attr_type = self.current_type.get_attribute(node.id).type

        if not inf_type.conforms_to(attr_type):
            error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (inf_type.name, attr_type.name)
            self.errors.append(HulkSemanticError(error_text))

        return attr_type

    @visitor.when(hulk_nodes.MethodDeclarationNode)
    def visit(self, node: hulk_nodes.MethodDeclarationNode):
        self.current_method = self.current_type.get_method(node.id)

        return_type = self.visit(node.expr)

        if self.current_type.parent is None:
            return return_type

        # Check if override is correct
        try:
            parent_method = self.current_type.parent.get_method(node.id)
        except HulkSemanticError:
            parent_method = None

        if parent_method is None:
            return return_type

        error_text = HulkSemanticError.WRONG_SIGNATURE % parent_method
        if parent_method.return_type != return_type:
            self.errors.append(HulkSemanticError(error_text))
            return_type = types.ErrorType()
        if len(parent_method.param_types) != len(self.current_method.param_types):
            self.errors.append(HulkSemanticError(error_text))
            return_type = types.ErrorType()

        for i in range(len(parent_method.param_types)):
            if parent_method.param_types[i] != self.current_method.param_types[i]:
                self.errors.append(HulkSemanticError(error_text))
                self.current_method.param_types[i] = types.ErrorType()
                return_type = types.ErrorType()

        self.current_method = None

        return return_type

    @visitor.when(hulk_nodes.FunctionDeclarationNode)
    def visit(self, node: hulk_nodes.FunctionDeclarationNode):
        function: Function = self.context.get_function(node.id)

        inf_return_type = self.visit(node.expr)

        if not inf_return_type.conforms_to(function.return_type):
            error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (inf_return_type.name, function.return_type.name)
            self.errors.append(HulkSemanticError(error_text))
            return types.ErrorType()

        return function.return_type

    @visitor.when(hulk_nodes.ExpressionBlockNode)
    def visit(self, node: hulk_nodes.ExpressionBlockNode):
        expr_type = types.ErrorType()

        for expr in node.expressions:
            expr_type = self.visit(expr)
        return expr_type

    @visitor.when(hulk_nodes.VarDeclarationNode)
    def visit(self, node: hulk_nodes.VarDeclarationNode):
        scope = node.scope

        inf_type = self.visit(node.expr)
        var_type = scope.find_variable(node.id).type

        if not inf_type.conforms_to(var_type):
            error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (inf_type.name, var_type.name)
            self.errors.append(HulkSemanticError(error_text))
            var_type = types.ErrorType()

        return var_type

    @visitor.when(hulk_nodes.LetInNode)
    def visit(self, node: hulk_nodes.LetInNode):

        for declaration in node.var_declarations:
            self.visit(declaration)

        return self.visit(node.body)

    @visitor.when(hulk_nodes.DestructiveAssignmentNode)
    def visit(self, node: hulk_nodes.DestructiveAssignmentNode):
        new_type = self.visit(node.expr)
        old_type = self.visit(node.target)

        if old_type.name == 'Self':
            self.errors.append(HulkSemanticError(HulkSemanticError.SELF_IS_READONLY))
            return types.ErrorType()

        if not new_type.conforms_to(old_type):
            error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (new_type.name, old_type.name)
            self.errors.append(HulkSemanticError(error_text))
            return types.ErrorType()

        return old_type

    @visitor.when(hulk_nodes.ConditionalNode)
    def visit(self, node: hulk_nodes.ConditionalNode):
        cond_types = [self.visit(cond) for cond in node.conditions]

        for cond_type in cond_types:
            if cond_type != types.BoolType():
                error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (cond_type.name, types.BoolType().name)
                self.errors.append(HulkSemanticError(error_text))

        expr_types = [self.visit(expression) for expression in node.expressions]

        else_type = self.visit(node.default_expr)

        return types.get_lowest_common_ancestor(expr_types + [else_type])

    @visitor.when(hulk_nodes.WhileNode)
    def visit(self, node: hulk_nodes.WhileNode):
        cond_type = self.visit(node.condition)

        if cond_type != types.BoolType():
            error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (cond_type.name, types.BoolType().name)
            self.errors.append(HulkSemanticError(error_text))

        return self.visit(node.expression)

    @visitor.when(hulk_nodes.ForNode)
    def visit(self, node: hulk_nodes.ForNode):
        ttype = self.visit(node.iterable)
        iterable_protocol = self.context.get_protocol('Iterable')

        if not ttype.conforms_to(iterable_protocol):
            error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (ttype.name, iterable_protocol.name)
            self.errors.append(HulkSemanticError(error_text))

        return self.visit(node.expression)

    @visitor.when(hulk_nodes.FunctionCallNode)
    def visit(self, node: hulk_nodes.FunctionCallNode):
        args_types = [self.visit(arg) for arg in node.args]

        try:
            function = self.context.get_function(node.idx)
        except HulkSemanticError as e:
            self.errors.append(e)
            return types.ErrorType()

        if len(args_types) != len(function.param_types):
            error_text = HulkSemanticError.EXPECTED_ARGUMENTS % (
                len(function.param_types), len(args_types), function.name)
            self.errors.append(HulkSemanticError(error_text))
            return types.ErrorType()

        for arg_type, param_type in zip(args_types, function.param_types):
            if not arg_type.conforms_to(param_type):
                error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (arg_type.name, param_type.name)
                self.errors.append(HulkSemanticError(error_text))
                return types.ErrorType()

        return function.return_type

    @visitor.when(hulk_nodes.MethodCallNode)
    def visit(self, node: hulk_nodes.MethodCallNode):
        args_types = [self.visit(arg) for arg in node.args]

        scope = node.scope
        # todo
        if not scope.is_defined(node.obj):
            obj_type = self.visit(node.obj)
        else:
            obj_type = scope.find_variable(node.obj).type

        if isinstance(obj_type, types.ErrorType):
            return types.ErrorType()

        try:
            if obj_type == types.SelfType():
                method = self.current_type.get_method(node.method)
            else:
                method = obj_type.get_method(node.method)
        except HulkSemanticError as e:
            self.errors.append(e)
            return types.ErrorType()

        if len(args_types) != len(method.param_types):
            error_text = HulkSemanticError.EXPECTED_ARGUMENTS % (len(method.param_types), len(args_types), method.name)
            self.errors.append(HulkSemanticError(error_text))
            return types.ErrorType()

        for arg_type, param_type in zip(args_types, method.param_types):
            if not arg_type.conforms_to(param_type):
                error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (arg_type.name, param_type.name)
                self.errors.append(HulkSemanticError(error_text))
                return types.ErrorType()

        return method.return_type

    @visitor.when(hulk_nodes.BaseCallNode)
    def visit(self, node: hulk_nodes.BaseCallNode):
        if self.current_method is None:
            self.errors.append(HulkSemanticError(HulkSemanticError.BASE_OUTSIDE_METHOD))
            return types.ErrorType()

        try:
            # todo new function
            method = self.current_type.parent.get_method(self.current_method.name)
            node.method_name = self.current_method.name
            node.parent_type = self.current_type.parent
        except HulkSemanticError:
            error_text = HulkSemanticError.METHOD_NOT_DEFINED % self.current_method.name
            self.errors.append(HulkSemanticError(error_text))
            return types.ErrorType()

        args_types = [self.visit(arg) for arg in node.args]

        if len(args_types) != len(method.param_types):
            error_text = HulkSemanticError.EXPECTED_ARGUMENTS % (len(method.param_types), len(args_types), method.name)
            self.errors.append(HulkSemanticError(error_text))
            return types.ErrorType()

        for arg_type, param_type in zip(args_types, method.param_types):
            if not arg_type.conforms_to(param_type):
                error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (arg_type.name, param_type.name)
                self.errors.append(HulkSemanticError(error_text))
                return types.ErrorType()

        return method.return_type

    @visitor.when(hulk_nodes.AttributeCallNode)
    def visit(self, node: hulk_nodes.AttributeCallNode):
        scope = node.scope

        # todo
        if not scope.is_defined(node.obj):
            obj_type = self.visit(node.obj)
        else:
            obj_type = scope.find_variable(node.obj).type

        if isinstance(obj_type, types.ErrorType):
            return types.ErrorType()

        if obj_type == types.SelfType():
            try:
                attr = self.current_type.get_attribute(node.attribute)
                return attr.type
            except HulkSemanticError as e:
                self.errors.append(e)
                return types.ErrorType()
        else:
            self.errors.append(HulkSemanticError("Cannot access an attribute from a non-self object"))
            return types.ErrorType()

    @visitor.when(hulk_nodes.IsNode)
    def visit(self, node: hulk_nodes.IsNode):
        self.visit(node.expression)
        bool_type = self.context.get_type('Boolean')

        try:
            self.context.get_type_or_protocol(node.ttype)
        except HulkSemanticError as e:
            self.errors.append(e)

        return bool_type

    @visitor.when(hulk_nodes.AsNode)
    def visit(self, node: hulk_nodes.AsNode):
        expression_type = self.visit(node.expression)

        try:
            cast_type = self.context.get_type_or_protocol(node.ttype)
        except HulkSemanticError as e:
            self.errors.append(e)
            cast_type = types.ErrorType()

        if not expression_type.conforms_to(cast_type) and not cast_type.conforms_to(expression_type):
            error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (expression_type.name, cast_type.name)
            self.errors.append(HulkSemanticError(error_text))
            return types.ErrorType()

        return cast_type

    @visitor.when(hulk_nodes.ArithmeticExpressionNode)
    def visit(self, node: hulk_nodes.ArithmeticExpressionNode):
        number_type = self.context.get_type('Number')

        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if not left_type == types.NumberType() or not right_type == types.NumberType():
            error_text = HulkSemanticError.INVALID_OPERATION % (node.operator, left_type.name, right_type.name)
            self.errors.append(HulkSemanticError(error_text))
            return types.ErrorType()

        return number_type

    @visitor.when(hulk_nodes.InequalityExpressionNode)
    def visit(self, node: hulk_nodes.ArithmeticExpressionNode):
        bool_type = self.context.get_type('Boolean')

        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if not left_type == types.NumberType() or not right_type == types.NumberType():
            error_text = HulkSemanticError.INVALID_OPERATION % (node.operator, left_type.name, right_type.name)
            self.errors.append(HulkSemanticError(error_text))
            return types.ErrorType()

        return bool_type

    @visitor.when(hulk_nodes.BoolBinaryExpressionNode)
    def visit(self, node: hulk_nodes.BoolBinaryExpressionNode):
        bool_type = self.context.get_type('Boolean')

        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if not left_type == types.BoolType() or not right_type == types.BoolType():
            error_text = HulkSemanticError.INVALID_OPERATION % (node.operator, left_type.name, right_type.name)
            self.errors.append(HulkSemanticError(error_text))
            return types.ErrorType()

        return bool_type

    @visitor.when(hulk_nodes.StrBinaryExpressionNode)
    def visit(self, node: hulk_nodes.StrBinaryExpressionNode):
        string_type = self.context.get_type('String')
        object_type = self.context.get_type('Object')

        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if not left_type.conforms_to(object_type) or not right_type.conforms_to(object_type):
            error_text = HulkSemanticError.INVALID_OPERATION % (node.operator, left_type.name, right_type.name)
            self.errors.append(HulkSemanticError(error_text))
            return types.ErrorType()

        return string_type

    @visitor.when(hulk_nodes.EqualityExpressionNode)
    def visit(self, node: hulk_nodes.ArithmeticExpressionNode):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if not left_type.conforms_to(right_type) and not right_type.conforms_to(left_type):
            error_text = HulkSemanticError.INVALID_OPERATION % (node.operator, left_type.name, right_type.name)
            self.errors.append(HulkSemanticError(error_text))
            return types.ErrorType()

        return self.context.get_type('Boolean')

    @visitor.when(hulk_nodes.NegNode)
    def visit(self, node: hulk_nodes.NegNode):
        operand_type = self.visit(node.operand, )
        number_type = self.context.get_type('Number')

        if operand_type != types.NumberType():
            error_text = HulkSemanticError.INVALID_UNARY_OPERATION % (node.operator, operand_type.name)
            self.errors.append(HulkSemanticError(error_text))
            return number_type

        return number_type

    @visitor.when(hulk_nodes.NotNode)
    def visit(self, node: hulk_nodes.NotNode):
        operand_type = self.visit(node.operand)
        bool_type = self.context.get_type('Boolean')

        if operand_type != types.BoolType():
            error_text = HulkSemanticError.INVALID_UNARY_OPERATION % (node.operator, operand_type.name)
            self.errors.append(HulkSemanticError(error_text))
            return types.ErrorType()

        return bool_type

    @visitor.when(hulk_nodes.ConstantBoolNode)
    def visit(self, node: hulk_nodes.ConstantBoolNode):
        return self.context.get_type('Boolean')

    @visitor.when(hulk_nodes.ConstantNumNode)
    def visit(self, node: hulk_nodes.ConstantNumNode):
        return self.context.get_type('Number')

    @visitor.when(hulk_nodes.ConstantStringNode)
    def visit(self, node: hulk_nodes.ConstantStringNode):
        return self.context.get_type('String')

    @visitor.when(hulk_nodes.VariableNode)
    def visit(self, node: hulk_nodes.VariableNode):
        scope = node.scope

        # todo
        if not scope.is_defined(node.lex):
            error_text = HulkSemanticError.VARIABLE_NOT_DEFINED % node.lex
            self.errors.append(HulkSemanticError(error_text))
            return types.ErrorType()

        var = scope.find_variable(node.lex)
        return var.type

    @visitor.when(hulk_nodes.TypeInstantiationNode)
    def visit(self, node: hulk_nodes.TypeInstantiationNode):
        try:
            ttype = self.context.get_type(node.idx)
        except HulkSemanticError as e:
            self.errors.append(e)
            return types.ErrorType()

        args_types = [self.visit(arg) for arg in node.args]

        if len(args_types) != len(ttype.params_types):
            error_text = HulkSemanticError.EXPECTED_ARGUMENTS % (len(ttype.params_types), len(args_types), ttype.name)
            self.errors.append(HulkSemanticError(error_text))
            return types.ErrorType()

        for arg_type, param_type in zip(args_types, ttype.params_types):
            if not arg_type.conforms_to(param_type):
                error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (arg_type.name, param_type.name)
                self.errors.append(HulkSemanticError(error_text))
                return types.ErrorType()

        return ttype

    # todo error type and auto type
    @visitor.when(hulk_nodes.VectorInitializationNode)
    def visit(self, node: hulk_nodes.VectorInitializationNode):
        elements_types = [self.visit(element) for element in node.elements]
        lca = types.get_lowest_common_ancestor(elements_types)
        return types.VectorType(lca)

    @visitor.when(hulk_nodes.VectorComprehensionNode)
    def visit(self, node: hulk_nodes.VectorComprehensionNode):
        ttype = self.visit(node.iterable)
        iterable_protocol = self.context.get_protocol('Iterable')

        return_type = self.visit(node.selector)

        if not ttype.conforms_to(iterable_protocol):
            error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (ttype.name, iterable_protocol.name)
            self.errors.append(HulkSemanticError(error_text))
            return types.ErrorType()

        # todo fix this. Fixed.
        return types.VectorType(return_type)

    @visitor.when(hulk_nodes.IndexingNode)
    def visit(self, node: hulk_nodes.IndexingNode):
        number_type = self.context.get_type('Number')

        index_type = self.visit(node.index)
        if index_type != number_type:
            error_text = HulkSemanticError.INCOMPATIBLE_TYPES % (index_type.name, number_type.name)
            self.errors.append(HulkSemanticError(error_text))
            return types.ErrorType()

        obj_type = self.visit(node.obj)

        if obj_type.is_error():
            return types.ErrorType()

        if not isinstance(obj_type, types.VectorType):
            error_text = HulkSemanticError.INVALID_UNARY_OPERATION % ('[]', obj_type.name)
            self.errors.append(HulkSemanticError(error_text))
            return types.ErrorType()

        return obj_type.get_element_type()
