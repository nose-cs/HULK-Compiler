from abc import ABC


# Depth 0
class Node(ABC):
    pass


# -------------------------------------------------------------------------------------------------------------------- #

# Depth 1

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


# -------------------------------------------------------------------------------------------------------------------- #

# Depth 2

# Statements
class FunctionDeclarationNode(StatementNode):
    def __init__(self, idx, args, expr):
        super().__init__()
        self.id = idx
        self.args = args
        self.expr = expr


class TypeDeclarationNode(StatementNode):
    def __init__(self):
        super().__init__()
        # todo add type declaration
        pass


class ProtocolDeclaration(StatementNode):
    def __init__(self):
        super().__init__()
        # todo add protocol declaration
        pass


# Expression
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
    def __init__(self, conditions, expressions, default_expr):
        """
        :param conditions: list of conditions
        :param expressions: list of expressions, i-th expression is executed if i-th condition is true
        :param default_expr: default expression (else)
        """
        super().__init__()
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


class VarDeclarationNode(ExpressionNode):
    def __init__(self, idx, expr):
        super().__init__()
        self.id = idx
        self.expr = expr


class LetInNode(ExpressionNode):
    def __init__(self, var_declarations, body):
        super().__init__()
        self.var_declarations = var_declarations
        self.body = body


# -------------------------------------------------------------------------------------------------------------------- #

# Depth 3

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


# String
class ConcatNode(BinaryExpressionNode):
    pass


class ConcatWithSpaceBetweenNode(BinaryExpressionNode):
    pass


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


# built-in arithmetic functions

class SqrtNode(UnaryExpressionNode):
    pass


class SinNode(UnaryExpressionNode):
    pass


class CosNode(UnaryExpressionNode):
    pass


class ExpNode(UnaryExpressionNode):
    pass


class LogNode(BinaryExpressionNode):
    pass


class RandNode(ExpressionNode):
    pass


# -------------------------------------------------------------------------------------------------------------------- #

# Depth4

# Constants
class PiConstantNode(ConstantNumNode):
    def __init__(self):
        super().__init__('PI')


class EConstantNode(ConstantNumNode):
    def __init__(self):
        super().__init__('E')
