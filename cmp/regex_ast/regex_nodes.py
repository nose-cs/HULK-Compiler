from lexer.build_nfa import BuildNFA

class Node:
    def evaluate(self):
        raise NotImplementedError()

class CharNode(Node):
    def __init__(self, token):
        self.token = token
        
    def evaluate(self):
        return BuildNFA.build_basic_nfa(self.token)        
    
class RegexNode(Node):
    def __init__(self, concat) -> None:
        self.nodes = concat


class BinaryNode(Node):
    def __init__(self, left:Node, right:Node):
        self.left = left
        self.right = right
        
    def evaluate(self):
        lvalue = self.left.evaluate()
        rvalue = self.right.evaluate()
        return self.operate(lvalue, rvalue)
    
    @staticmethod
    def operate(lvalue, rvalue):
        raise NotImplementedError()

class KleeneNode(Node):
    def __init__(self, child: Node) -> None:
        self.child = child

    def evaluate(self):
        value = self.child.evaluate()
        return BuildNFA.kleene_closure(value)

class OrNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        return BuildNFA.join_nfas(lvalue, rvalue)
    
class ConcatNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        return BuildNFA.concatenate_nfas(lvalue, rvalue)
