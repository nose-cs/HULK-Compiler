from abc import ABC
from typing import List, Tuple

from src.semantics.utils import Scope


# ---------------------------------------------------Depth 0---------------------------------------------------------- #
class Node(ABC):
    def __init__(self):
        self.scope: Scope


# ---------------------------------------------------Depth 1---------------------------------------------------------- #

class ProgramNode(Node):
    def __init__(self, declarations, expression):
        super().__init__()
        self.declarations = declarations
        self.expression = expression


class ExpressionNode(Node):
    pass


class DeclarationNode(Node):
    pass


# ---------------------------------------------------Depth 2---------------------------------------------------------- #

class FunctionDeclarationNode(DeclarationNode):
    def __init__(self, idx, params, expr, return_type=None):
        super().__init__()
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
        super().__init__()
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
        super().__init__()
        self.idx = idx
        self.methods_signature = methods_signature
        self.parent = parent


class MethodDeclarationNode(DeclarationNode):
    def __init__(self, idx, params, expr, return_type=None):
        super().__init__()
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
        super().__init__()
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
        super().__init__()
        self.id = idx
        self.expr = expr
        self.attribute_type = attribute_type


class TypeInstantiationNode(ExpressionNode):
    def __init__(self, idx, args):
        super().__init__()
        self.idx = idx
        self.args = args


class ExpressionBlockNode(ExpressionNode):
    def __init__(self, expressions):
        super().__init__()
        self.expressions = expressions


class DestructiveAssignmentNode(ExpressionNode):
    def __init__(self, target, expr):
        super().__init__()
        self.target = target
        self.expr = expr


class AtomicNode(ExpressionNode, ABC):
    def __init__(self, lex):
        super().__init__()
        self.lex = lex


class BinaryExpressionNode(ExpressionNode, ABC):
    def __init__(self, left, right):
        super().__init__()
        self.left = left
        self.right = right
        self.operator = None


class UnaryExpressionNode(ExpressionNode, ABC):
    def __init__(self, operand):
        super().__init__()
        self.operand = operand
        self.operator = None


class ConditionalNode(ExpressionNode):
    def __init__(self, cond_expr: List[Tuple], default_expr):
        super().__init__()
        conditions, expressions = zip(*cond_expr)
        self.conditions = conditions
        self.expressions = expressions
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


class VarDeclarationNode(DeclarationNode):
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


class VectorInitializationNode(ExpressionNode):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements


class VectorComprehensionNode(ExpressionNode):
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


class FunctionCallNode(ExpressionNode):
    def __init__(self, idx, args):
        super().__init__()
        self.idx = idx
        self.args = args


class AttributeCallNode(ExpressionNode):
    def __init__(self, obj, attribute):
        super().__init__()
        self.obj = obj
        self.attribute = attribute


class MethodCallNode(ExpressionNode):
    def __init__(self, obj, method, args):
        super().__init__()
        self.obj = obj
        self.method = method
        self.args = args


class BaseCallNode(ExpressionNode):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.method_name = None
        self.parent_type = None

class IndexingNode(ExpressionNode):
    def __init__(self, obj, index):
        super().__init__()
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
