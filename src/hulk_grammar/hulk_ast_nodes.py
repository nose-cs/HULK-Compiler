from abc import ABC
from typing import List, Tuple

from src.semantics.utils import Scope


# ---------------------------------------------------Depth 0---------------------------------------------------------- #
class Node(ABC):
    def __init__(self):
        self.scope: Scope = None


# ---------------------------------------------------Depth 1---------------------------------------------------------- #

class ProgramNode(Node):
    def __init__(self, declarations, expression):
        self.declarations = declarations
        self.expression = expression


class ExpressionNode(Node, ABC):
    pass


class DeclarationNode(Node, ABC):
    pass


# ---------------------------------------------------Depth 2---------------------------------------------------------- #

class FunctionDeclarationNode(DeclarationNode):
    def __init__(self, idx, params, expr, return_type=None):
        if len(params) > 0:
            params_ids, params_types = zip(*params)
        else:
            params_ids, params_types = [], []
        self.id = idx
        self.params_ids = params_ids
        self.params_types = params_types
        self.expr = expr
        self.return_type = return_type


class TypeDeclarationNode(DeclarationNode):
    def __init__(self, idx, params, body, parent, parent_args=None):
        if params and len(params) > 0:
            params_ids, params_types = zip(*params)
        elif params and len(params) == 0:
            params_ids, params_types = [], []
        else:
            params_ids, params_types = None, None
        self.idx = idx
        self.methods = [method for method in body if isinstance(method, MethodDeclarationNode)]
        self.attributes = [attribute for attribute in body if isinstance(attribute, AttributeDeclarationNode)]
        self.params_ids = params_ids
        self.params_types = params_types
        self.parent = parent
        self.parent_args = parent_args


class ProtocolDeclarationNode(DeclarationNode):
    def __init__(self, idx, methods_signature, parent):
        self.idx = idx
        self.methods_signature = methods_signature
        self.parent = parent


class MethodDeclarationNode(DeclarationNode):
    def __init__(self, idx, params, expr, return_type=None):
        if len(params) > 0:
            params_ids, params_types = zip(*params)
        else:
            params_ids, params_types = [], []
        self.id = idx
        self.params_ids = params_ids
        self.params_types = params_types
        self.expr = expr
        self.return_type = return_type


class MethodSignatureDeclarationNode(DeclarationNode):
    def __init__(self, idx, params, return_type):
        if len(params) > 0:
            params_ids, params_types = zip(*params)
        else:
            params_ids, params_types = [], []
        self.id = idx
        self.params_ids = params_ids
        self.params_types = params_types
        self.return_type = return_type


class AttributeDeclarationNode(DeclarationNode):
    def __init__(self, idx, expr, attribute_type=None):
        self.id = idx
        self.expr = expr
        self.attribute_type = attribute_type


class TypeInstantiationNode(ExpressionNode):
    def __init__(self, idx, args):
        self.idx = idx
        self.args = args


class ExpressionBlockNode(ExpressionNode):
    def __init__(self, expressions):
        self.expressions = expressions


class DestructiveAssignmentNode(ExpressionNode):
    def __init__(self, target, expr):
        self.target = target
        self.expr = expr


class AtomicNode(ExpressionNode, ABC):
    def __init__(self, lex):
        self.lex = lex


class BinaryExpressionNode(ExpressionNode, ABC):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.operator = None


class UnaryExpressionNode(ExpressionNode, ABC):
    def __init__(self, operand):
        self.operand = operand
        self.operator = None


class ConditionalNode(ExpressionNode):
    def __init__(self, cond_expr: List[Tuple], default_expr):
        conditions, expressions = zip(*cond_expr)
        self.conditions = conditions
        self.expressions = expressions
        self.default_expr = default_expr


class WhileNode(ExpressionNode):
    def __init__(self, condition, expression):
        self.condition = condition
        self.expression = expression


class ForNode(ExpressionNode):
    def __init__(self, var, iterable, expression):
        self.var = var
        self.iterable = iterable
        self.expression = expression


class VarDeclarationNode(DeclarationNode):
    def __init__(self, idx, expr, var_type=None):
        self.id = idx
        self.expr = expr
        self.var_type = var_type


class LetInNode(ExpressionNode):
    def __init__(self, var_declarations, body):
        self.var_declarations = var_declarations
        self.body = body


class VectorInitializationNode(ExpressionNode):
    def __init__(self, elements):
        self.elements = elements


class VectorComprehensionNode(ExpressionNode):
    def __init__(self, selector, var, iterable):
        self.selector = selector
        self.var = var
        self.iterable = iterable


class IsNode(ExpressionNode):
    def __init__(self, expression, ttype):
        self.expression = expression
        self.ttype = ttype


class AsNode(ExpressionNode):
    def __init__(self, expression, ttype):
        self.expression = expression
        self.ttype = ttype


class FunctionCallNode(ExpressionNode):
    def __init__(self, idx, args):
        self.idx = idx
        self.args = args


class AttributeCallNode(ExpressionNode):
    def __init__(self, obj, attribute):
        self.obj = obj
        self.attribute = attribute


class MethodCallNode(ExpressionNode):
    def __init__(self, obj, method, args):
        self.obj = obj
        self.method = method
        self.args = args


class IndexingNode(ExpressionNode):
    def __init__(self, obj, index):
        self.obj = obj
        self.index = index


# ---------------------------------------------------Depth 3---------------------------------------------------------- #

class ConstantNumNode(AtomicNode):
    pass


class ConstantBoolNode(AtomicNode):
    pass


class ConstantStringNode(AtomicNode):
    pass


class VariableNode(AtomicNode):
    pass


class StrBinaryExpressionNode(BinaryExpressionNode, ABC):
    pass


class BoolBinaryExpressionNode(BinaryExpressionNode, ABC):
    pass


class InequalityExpressionNode(BinaryExpressionNode, ABC):
    pass


class ArithmeticExpressionNode(BinaryExpressionNode, ABC):
    pass


class EqualityExpressionNode(BinaryExpressionNode, ABC):
    pass


class NotNode(UnaryExpressionNode):
    pass


class NegNode(UnaryExpressionNode):
    pass


# ---------------------------------------------------Depth 4---------------------------------------------------------- #
class ConcatNode(StrBinaryExpressionNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = 'concat (@, @@)'


class OrNode(BoolBinaryExpressionNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '|'


class AndNode(BoolBinaryExpressionNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '&'


class LessThanNode(InequalityExpressionNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '<'


class GreaterThanNode(InequalityExpressionNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '>'


class LessOrEqualNode(InequalityExpressionNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '<='


class GreaterOrEqualNode(InequalityExpressionNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '>='


class PlusNode(ArithmeticExpressionNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '+'


class MinusNode(ArithmeticExpressionNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '-'


class StarNode(ArithmeticExpressionNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '*'


class DivNode(ArithmeticExpressionNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '/'


class ModNode(ArithmeticExpressionNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '%'


class PowNode(ArithmeticExpressionNode):
    def __init__(self, left, right, operator):
        super().__init__(left, right)
        self.operator = operator


class EqualNode(EqualityExpressionNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '=='


class NotEqualNode(EqualityExpressionNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.operator = '!='
