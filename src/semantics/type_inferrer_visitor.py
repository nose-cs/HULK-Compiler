from typing import List

import src.hulk_grammar.hulk_ast_nodes as hulk_nodes
import src.semantics.types as types
import src.visitor as visitor
from src.errors import SemanticError
from src.semantics.utils import Scope, Context, Function


# todo destructive assignment
class TypeInferrer(object):
    def __init__(self, context, errors=None) -> None:
        if errors is None:
            errors = []
        self.context: Context = context
        self.current_type = None
        self.current_method = None
        self.errors: List[SemanticError] = errors
        self.had_changed = False

    def assign_auto_type(self, node: hulk_nodes.Node, scope: Scope, inf_type: types.Type | types.Protocol):
        """
        Add the inferred type to the variable in the scope
        :param node: The node that was inferred
        :param scope: The scope where the variable is
        :param inf_type: The inferred type
        :rtype: None
        """
        if inf_type == types.AutoType():
            return
        if isinstance(node, hulk_nodes.VariableNode) and scope.is_defined(node.lex):
            var_info = scope.find_variable(node.lex)
            if var_info.type != types.AutoType() or var_info.type.is_error():
                return
            var_info.inferred_types.append(inf_type)
            self.had_changed = True

    @visitor.on('node')
    def visit(self, node: hulk_nodes.Node):
        pass

    @visitor.when(hulk_nodes.ProgramNode)
    def visit(self, node: hulk_nodes.ProgramNode):
        for declaration in node.declarations:
            self.visit(declaration)

        self.visit(node.expression)

        if self.had_changed:
            self.had_changed = False
            self.visit(node)

        inference_errors = self.context.inference_errors() + node.scope.inference_errors()
        self.errors.extend(inference_errors)

    @visitor.when(hulk_nodes.TypeDeclarationNode)
    def visit(self, node: hulk_nodes.TypeDeclarationNode):
        self.current_type = self.context.get_type(node.idx)

        const_scope = node.scope.children[0]

        for attr in node.attributes:
            self.visit(attr)

        # Check if we could infer some params types
        for i in range(len(self.current_type.params_types)):
            if (self.current_type.params_types[i] == types.AutoType()
                    and not self.current_type.params_types[i].is_error()):
                local_var = const_scope.find_variable(self.current_type.params_names[i])
                if local_var.inferred_types:
                    new_type = types.get_most_specialized_type(local_var.inferred_types)
                    self.current_type.params_types[i] = new_type
                    # todo try catch: is any error
                    local_var.set_type_and_clear_inference_types_list(new_type)
                    if new_type.is_error():
                        param_name = self.current_type.params_names[i]
                        self.errors.append(SemanticError(SemanticError.INCONSISTENT_USE % param_name))

        for expr in node.parent_args:
            self.visit(expr)

        # Infer the params types and return type of the methods
        for method in node.methods:
            self.visit(method)

        self.current_type = None

    @visitor.when(hulk_nodes.AttributeDeclarationNode)
    def visit(self, node: hulk_nodes.AttributeDeclarationNode):
        inf_type = self.visit(node.expr)

        attribute = self.current_type.get_attribute(node.id)

        if attribute.type.is_error():
            attr_type = types.ErrorType()
        elif attribute.type != types.AutoType():
            attr_type = attribute.type
        else:
            attr_type = inf_type

        attribute.type = attr_type
        return attr_type

    @visitor.when(hulk_nodes.MethodDeclarationNode)
    def visit(self, node: hulk_nodes.MethodDeclarationNode):
        self.current_method = self.current_type.get_method(node.id)

        method_scope = node.expr.scope
        return_type = self.visit(node.expr)

        if self.current_method.return_type == types.AutoType():
            self.current_method.return_type = return_type

        # Check if we could infer some params types
        for i in range(len(self.current_method.param_types)):
            if (self.current_method.param_types[i] == types.AutoType()
                    and not self.current_method.param_types[i].is_error()):
                local_var = method_scope.find_variable(self.current_method.param_names[i])
                if local_var.inferred_types:
                    new_type = types.get_most_specialized_type(local_var.inferred_types)
                    self.current_method.param_types[i] = new_type
                    local_var.set_type_and_clear_inference_types_list(new_type)
                    if new_type.is_error():
                        self.errors.append(SemanticError(SemanticError.INCONSISTENT_USE))

        self.current_method = None

        return return_type

    @visitor.when(hulk_nodes.FunctionDeclarationNode)
    def visit(self, node: hulk_nodes.FunctionDeclarationNode):
        function: Function = self.context.get_function(node.id)

        return_type = self.visit(node.expr)

        if function.return_type == types.AutoType():
            function.return_type = return_type

        expr_scope = node.expr.scope

        # Check if we could infer some params types
        for i in range(len(function.param_types)):
            if function.param_types[i] == types.AutoType() and not function.param_types[i].is_error():
                local_var = expr_scope.find_variable(function.param_names[i])
                if local_var.inferred_types:
                    new_type = types.get_most_specialized_type(local_var.inferred_types)
                    function.param_types[i] = new_type
                    local_var.set_type_and_clear_inference_types_list(new_type)
                    if new_type.is_error():
                        self.errors.append(SemanticError(SemanticError.INCONSISTENT_USE))

        return return_type

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

        var = scope.find_variable(node.id)
        var.type = var.type if var.type != types.AutoType() or var.type.is_error() else inf_type

        return var.type

    @visitor.when(hulk_nodes.LetInNode)
    def visit(self, node: hulk_nodes.LetInNode):

        for declaration in node.var_declarations:
            self.visit(declaration)

        return_type = self.visit(node.body)

        return return_type

    @visitor.when(hulk_nodes.DestructiveAssignmentNode)
    def visit(self, node: hulk_nodes.DestructiveAssignmentNode):
        self.visit(node.expr)
        old_type = self.visit(node.target)
        return old_type

    @visitor.when(hulk_nodes.ConditionalNode)
    def visit(self, node: hulk_nodes.ConditionalNode):
        cond_types = [self.visit(cond) for cond in node.conditions]

        # todo if any is not bool return ErrorType

        expr_types = [self.visit(expression) for expression in node.expressions]

        else_type = self.visit(node.default_expr)

        return types.get_lowest_common_ancestor(expr_types + [else_type])

    @visitor.when(hulk_nodes.WhileNode)
    def visit(self, node: hulk_nodes.WhileNode):
        self.visit(node.condition)
        return self.visit(node.expression)

    @visitor.when(hulk_nodes.ForNode)
    def visit(self, node: hulk_nodes.ForNode):
        ttype = self.visit(node.iterable)
        iterable_protocol = self.context.get_protocol('Iterable')

        expr_scope = node.expression.scope
        variable = expr_scope.find_variable(node.var)

        # todo AutoType
        if ttype.conforms_to(iterable_protocol):
            element_type = ttype.get_method('current').return_type
            variable.type = element_type
        else:
            variable.type = types.ErrorType()

        return self.visit(node.expression)

    @visitor.when(hulk_nodes.FunctionCallNode)
    def visit(self, node: hulk_nodes.FunctionCallNode):
        scope = node.scope

        try:
            function = self.context.get_function(node.idx)
        except SemanticError:
            return types.ErrorType()

        for arg, param_type in zip(node.args, function.param_types):
            self.visit(arg)
            self.assign_auto_type(arg, scope, param_type)

        return function.return_type

    @visitor.when(hulk_nodes.BaseCallNode)
    def visit(self, node: hulk_nodes.BaseCallNode):
        scope = node.scope

        if self.current_method is None:
            return types.ErrorType()

        try:
            method = self.current_type.parent.get_method(self.current_method.name)
        except SemanticError:
            # todo visit args just for catch more errors
            return types.ErrorType()

        for arg, param_type in zip(node.args, method.param_types):
            self.visit(arg)
            self.assign_auto_type(arg, scope, param_type)

        return method.return_type

    @visitor.when(hulk_nodes.MethodCallNode)
    def visit(self, node: hulk_nodes.MethodCallNode):
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
        except SemanticError:
            return types.ErrorType()

        for arg, param_type in zip(node.args, method.param_types):
            self.visit(arg)
            self.assign_auto_type(arg, scope, param_type)

        return method.return_type

    @visitor.when(hulk_nodes.AttributeCallNode)
    def visit(self, node: hulk_nodes.AttributeCallNode):
        scope = node.scope

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
            except SemanticError:
                return types.ErrorType()
        else:
            # Can't access to a non-self attribute
            return types.ErrorType()

    @visitor.when(hulk_nodes.IsNode)
    def visit(self, node: hulk_nodes.IsNode):
        bool_type = self.context.get_type('Boolean')
        self.visit(node.expression)
        return bool_type

    @visitor.when(hulk_nodes.AsNode)
    def visit(self, node: hulk_nodes.AsNode):
        expr_type = self.visit(node.expression)
        cast_type = self.context.get_type_or_protocol(node.ttype)
        if not expr_type.conforms_to(cast_type) and not cast_type.conforms_to(expr_type):
            return types.ErrorType()
        if expr_type.is_error():
            return types.ErrorType()
        return cast_type

    @visitor.when(hulk_nodes.ArithmeticExpressionNode)
    def visit(self, node: hulk_nodes.ArithmeticExpressionNode):
        scope = node.scope

        number_type = self.context.get_type('Number')

        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if left_type == types.AutoType() and not left_type.is_error():
            self.assign_auto_type(node.left, scope, number_type)
        elif left_type != number_type or left_type.is_error():
            return types.ErrorType()

        if right_type == types.AutoType() and not right_type.is_error():
            self.assign_auto_type(node.right, scope, number_type)
        elif right_type != number_type or right_type.is_error():
            return types.ErrorType()

        return number_type

    @visitor.when(hulk_nodes.InequalityExpressionNode)
    def visit(self, node: hulk_nodes.ArithmeticExpressionNode):
        scope = node.scope

        bool_type = self.context.get_type('Boolean')
        number_type = self.context.get_type('Number')

        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if left_type == types.AutoType() and not left_type.is_error():
            self.assign_auto_type(node.left, scope, number_type)
        elif left_type != number_type or left_type.is_error():
            return types.ErrorType()

        if right_type == types.AutoType() and not right_type.is_error():
            self.assign_auto_type(node.right, scope, number_type)
        elif right_type != number_type or right_type.is_error():
            return types.ErrorType()

        return bool_type

    @visitor.when(hulk_nodes.BoolBinaryExpressionNode)
    def visit(self, node: hulk_nodes.BoolBinaryExpressionNode):
        scope = node.scope

        bool_type = self.context.get_type('Boolean')

        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if left_type == types.AutoType() and not left_type.is_error():
            self.assign_auto_type(node.left, scope, bool_type)
        elif left_type != bool_type or left_type.is_error():
            return types.ErrorType()

        if right_type == types.AutoType() and not right_type.is_error():
            self.assign_auto_type(node.right, scope, bool_type)
        elif right_type != bool_type or right_type.is_error():
            return types.ErrorType()

        return bool_type

    @visitor.when(hulk_nodes.StrBinaryExpressionNode)
    def visit(self, node: hulk_nodes.StrBinaryExpressionNode):
        scope = node.scope

        string_type = self.context.get_type('String')
        object_type = self.context.get_type('Object')

        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if left_type == types.AutoType() and not left_type.is_error():
            self.assign_auto_type(node.left, scope, object_type)
        elif left_type.is_error():
            return types.ErrorType()

        if right_type == types.AutoType() and not right_type.is_error():
            self.assign_auto_type(node.right, scope, object_type)
        elif right_type.is_error():
            return types.ErrorType()

        return string_type

    @visitor.when(hulk_nodes.EqualityExpressionNode)
    def visit(self, node: hulk_nodes.EqualityExpressionNode):
        bool_type = self.context.get_type('Boolean')

        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if not left_type.conforms_to(right_type) and not right_type.conforms_to(left_type):
            return types.ErrorType()

        return bool_type

    @visitor.when(hulk_nodes.NegNode)
    def visit(self, node: hulk_nodes.NegNode):
        scope = node.scope

        operand_type = self.visit(node.operand)
        number_type = self.context.get_type('Number')

        if operand_type == types.AutoType():
            self.assign_auto_type(node.operand, scope, number_type)
        elif operand_type != number_type or operand_type.is_error():
            return types.ErrorType()

        return number_type

    @visitor.when(hulk_nodes.NotNode)
    def visit(self, node: hulk_nodes.NotNode):
        scope = node.scope

        operand_type = self.visit(node.operand)
        bool_type = self.context.get_type('Boolean')

        if operand_type == types.AutoType() and not operand_type.is_error():
            self.assign_auto_type(node.operand, scope, bool_type)
        elif operand_type != bool_type or operand_type.is_error():
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

        if not scope.is_defined(node.lex):
            return types.ErrorType()

        var = scope.find_variable(node.lex)
        return var.type

    @visitor.when(hulk_nodes.TypeInstantiationNode)
    def visit(self, node: hulk_nodes.TypeInstantiationNode):
        try:
            ttype = self.context.get_type(node.idx)
        except SemanticError:
            return types.ErrorType()

        for arg in node.args:
            self.visit(arg)

        return ttype

    @visitor.when(hulk_nodes.VectorInitializationNode)
    def visit(self, node: hulk_nodes.VectorInitializationNode):
        elements_types = [self.visit(element) for element in node.elements]
        lca = types.get_lowest_common_ancestor(elements_types)
        return types.VectorType(lca)

    @visitor.when(hulk_nodes.VectorComprehensionNode)
    def visit(self, node: hulk_nodes.VectorComprehensionNode):
        ttype = self.visit(node.iterable)
        iterable_protocol = self.context.get_protocol('Iterable')

        selector_scope = node.selector.scope

        variable = selector_scope.find_variable(node.var)

        # todo ttype es autotype
        if ttype.conforms_to(iterable_protocol) and not ttype.is_error():
            element_type = ttype.get_method('current').return_type
            variable.type = element_type
        else:
            variable.type = types.ErrorType()

        return_type = self.visit(node.selector)

        return types.VectorType(return_type)

    @visitor.when(hulk_nodes.IndexingNode)
    def visit(self, node: hulk_nodes.IndexingNode):
        scope = node.scope

        number_type = self.context.get_type('Number')

        index_type = self.visit(node.index)
        obj_type = self.visit(node.obj)

        if index_type == types.AutoType() and not index_type.is_error():
            self.assign_auto_type(node.index, scope, number_type)
        elif index_type != number_type or index_type.is_error():
            return types.ErrorType()

        if obj_type.is_error():
            return types.ErrorType()

        if not isinstance(obj_type, types.VectorType):
            return types.ErrorType()

        return obj_type.get_element_type()
