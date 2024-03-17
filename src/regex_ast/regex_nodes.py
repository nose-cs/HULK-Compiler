class Node:
    def evaluate(self):
        raise NotImplementedError()


class CharNode(Node):
    def __init__(self, token):
        self.token = token


class RegexNode(Node):
    def __init__(self, concat) -> None:
        self.nodes = concat


class KleeneNode(Node):
    def __init__(self, child: Node) -> None:
        self.child = child


class OrNode(Node):
    def __init__(self, children: Node) -> None:
        self.children = children
