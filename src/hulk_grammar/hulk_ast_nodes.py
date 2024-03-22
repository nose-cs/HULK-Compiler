from abc import ABC
from typing import List, Tuple


# ---------------------------------------------------Depth 0---------------------------------------------------------- #
class Node(ABC):
    pass


# ---------------------------------------------------Depth 1---------------------------------------------------------- #

class ProgramNode(Node):
    def __init__(self, declarations, expression):
        self.declarations = declarations
        self.expression = expression


class ExpressionNode(Node):
    def __init__(self):
        pass


class StatementNode(Node):
    def __init__(self):
        pass


# ---------------------------------------------------Depth 2---------------------------------------------------------- #

# Statements
class FunctionDeclarationNode(StatementNode):
    def __init__(self, idx, params, expr, return_type=None):
        super().__init__()
        self.id = idx
        self.params = params
        self.expr = expr
        self.return_type = return_type


class TypeDeclarationNode(StatementNode):
    def __init__(self, idx, params, body, parent, parent_params=None):
        super().__init__()
        if parent_params is None:
            parent_params = []
        self.idx = idx
        self.body = body
        self.params = params
        self.parent = parent
        self.parent_params = parent_params


class ProtocolDeclaration(StatementNode):
    def __init__(self, idx, methods_signature, parent):
        super().__init__()
        self.idx = idx
        self.methods_signature = methods_signature
        self.parent = parent


class MethodDeclarationNode(StatementNode):
    def __init__(self, idx, params, expr, return_type=None):
        super().__init__()
        self.id = idx
        self.params = params
        self.expr = expr
        self.return_type = return_type


class MethodSignature(StatementNode):
    def __init__(self, idx, params, return_type):
        super().__init__()
        self.id = idx
        self.params = params
        self.return_type = return_type


class AttributeStatement(StatementNode):
    def __init__(self, idx, expr, attribute_type=None):
        super().__init__()
        self.id = idx
        self.expr = expr
        self.attribute_type = attribute_type


# Expressions
class ParamNode(ExpressionNode):
    def __init__(self, idx, param_type=None):
        super().__init__()
        self.id = idx
        self.var_type = param_type


class TypeInstantiationNode(ExpressionNode):
    def __init__(self, idx, args):
        super().__init__()
        self.idx = idx
        self.params = args


class ExpressionBlockNode(ExpressionNode):
    def __init__(self, expressions):
        super().__init__()
        self.expressions = expressions


class DestructiveAssignmentNode(ExpressionNode):
    def __init__(self, idx, expr):
        super().__init__()
        self.id = idx
        self.expr = expr


class AtomicNode(ExpressionNode):
    def __init__(self, lex):
        super().__init__()
        self.lex = lex


class BinaryExpressionNode(ExpressionNode):
    def __init__(self, left, right):
        super().__init__()
        self.left = left
        self.right = right


class UnaryExpressionNode(ExpressionNode):
    def __init__(self, operand):
        super().__init__()
        self.operand = operand


class ConditionalNode(ExpressionNode):
    def __init__(self, cond_expr: List[Tuple], default_expr):
        super().__init__()
        self.cond_expr = cond_expr
        self.default_expr = default_expr


class WhileNode(ExpressionNode):
    def __init__(self, condition, expression):
        super().__init__()
        self.condition = condition
        self.expression = expression


class ForNode(ExpressionNode):
    def __init__(self, var, iterable, expression):
        super().__init__()
        self.var = var
        self.iterable = iterable
        self.expression = expression


class VarDeclarationNode(ExpressionNode):
    def __init__(self, idx, expr, var_type=None):
        super().__init__()
        self.id = idx
        self.expr = expr
        self.var_type = var_type


class LetInNode(ExpressionNode):
    def __init__(self, var_declarations, body):
        super().__init__()
        self.var_declarations = var_declarations
        self.body = body


class VectorInitialization(ExpressionNode):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements


class VectorComprehension(ExpressionNode):
    def __init__(self, selector, var, iterable):
        super().__init__()
        self.selector = selector
        self.var = var
        self.iterable = iterable


class IsNode(ExpressionNode):
    def __init__(self, expression, ttype):
        super().__init__()
        self.expression = expression
        self.ttype = ttype


class AsNode(ExpressionNode):
    def __init__(self, expression, ttype):
        super().__init__()
        self.expression = expression
        self.ttype = ttype


# ---------------------------------------------------Depth 3---------------------------------------------------------- #

# Atomic
class ConstantNumNode(AtomicNode):
    pass


class ConstantBoolNode(AtomicNode):
    pass


class ConstantStringNode(AtomicNode):
    pass


class VariableNode(AtomicNode):
    pass


class CallNode(AtomicNode):
    def __init__(self, idx, args):
        super().__init__(idx)
        self.args = args


class AttributeCallNode(AtomicNode):
    def __init__(self, obj, attribute):
        super().__init__(f"{obj}.{attribute}")
        self.obj = obj
        self.attribute = attribute


class MethodCallNode(AtomicNode):
    def __init__(self, obj, method, args):
        super().__init__(f"{obj}.{method}")
        self.obj = obj
        self.method = method
        self.args = args


# String
class ConcatNode(BinaryExpressionNode):
    pass

    def concat_with(self, other):
        return ConcatNode(self, other)


# Boolean
class OrNode(BinaryExpressionNode):
    pass


class AndNode(BinaryExpressionNode):
    pass


class NotNode(UnaryExpressionNode):
    pass


# All types

class EqualNode(BinaryExpressionNode):
    pass


class NotEqualNode(BinaryExpressionNode):
    pass


# Arithmetic

class LessThanNode(BinaryExpressionNode):
    pass


class GreaterThanNode(BinaryExpressionNode):
    pass


class LessOrEqualNode(BinaryExpressionNode):
    pass


class GreaterOrEqualNode(BinaryExpressionNode):
    pass


class PlusNode(BinaryExpressionNode):
    pass


class MinusNode(BinaryExpressionNode):
    pass


class StarNode(BinaryExpressionNode):
    pass


class DivNode(BinaryExpressionNode):
    pass


class ModNode(BinaryExpressionNode):
    pass


class PowNode(BinaryExpressionNode):
    pass


class NegNode(UnaryExpressionNode):
    pass
