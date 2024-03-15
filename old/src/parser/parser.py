import sys
sys.path.insert(1, '..')

try:
    from utils import createAutomatonSLR1, create_SLR1_Table
except:
    from parser.utils import createAutomatonSLR1, create_SLR1_Table
class Node:
    def __init__(self, text, childs = [], evaluate = None) -> None:
        self.text = text
        self.childs = childs
        self.evaluateFun = evaluate

    def evaluate(self):
        return self.evaluateFun(self)

    def __str__(self) -> str:
        def print_tree(node, level=0):
            indent = "  " * level
            result = f"{indent}{node.text}"
            for child in node.childs:
                result += '\n' + print_tree(child, level + 1)
            return result

        return print_tree(self)

class ParserSLR1:
    def __init__(self, productions, non_terminals, terminals, start_symbol, getProductionEvaluate) -> None:
        dfa, states = createAutomatonSLR1(productions, non_terminals, start_symbol)
        self.table = create_SLR1_Table(productions, non_terminals, terminals, start_symbol, states)
        self.productions = productions
        self.non_terminals = non_terminals
        self.terminals = terminals
        self.start_symbol = start_symbol
        self.getProductionEvaluate = getProductionEvaluate

    def parse(self, tokens):
        stack = [0]
        tokens = [token for token in tokens]
        pointer = 0

        applied_productions = []

        while pointer < len(tokens):
            if self.table[tokens[pointer]][stack[-1]]:
                if self.table[tokens[pointer]][stack[-1]] == 'Accept!':
                    break

                elif isinstance(self.table[tokens[pointer]][stack[-1]], int):
                    stack.append(self.table[tokens[pointer]][stack[-1]])
                    pointer += 1
                
                else:
                    applied_productions.append(self.table[tokens[pointer]][stack[-1]])
                    head, index = self.table[tokens[pointer]][stack[-1]]

                    for i in range(len(self.productions[head][index])):
                        stack.pop()

                    stack.append(self.table[head][stack[-1]])

            else:
                raise Exception("Chain cannot be parsed")

        def makeTree(node : Node, applied_productions, non_terminals):
            if len(applied_productions) > 0:
                head, index = applied_productions.pop()

                node.childs = [Node(token) for token in self.productions[head][index]]
                node.childs.reverse()

                node.evaluateFun = self.getProductionEvaluate((head, index))

                for child in node.childs:
                    if child.text in non_terminals:
                        makeTree(child, applied_productions, non_terminals)

                node.childs.reverse()

        root = Node(applied_productions[-1][0])
        makeTree(root, applied_productions, self.non_terminals)
            
        return root