class Node:
    def evaluate(self):
        raise NotImplementedError()


class CharNode(Node):
    def __init__(self, token):
        self.token = token


class RegexNode(Node):
    def __init__(self, concat) -> None:
        self.nodes = concat


class BinaryNode(Node):
    def __init__(self, left: Node, right: Node):
        self.left = left
        self.right = right


class KleeneNode(Node):
    def __init__(self, child: Node) -> None:
        self.child = child


class OrNode(BinaryNode):
    pass


class ConcatNode(BinaryNode):
    pass
