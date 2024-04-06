import src.regex.regex_nodes as regex_nodes
import src.automaton_operations as regex_operations_automata
import src.visitor as visitor


class AutomataBuilderVisitor(object):
    @visitor.on('node')
    def visit(self, node: regex_nodes.Node):
        pass

    @visitor.when(regex_nodes.ConcatNode)
    def visit(self, node: regex_nodes.ConcatNode):
        acc = self.visit(node.nodes[0])
        for i in range(1, len(node.nodes)):
            acc = regex_operations_automata.concatenate_nfas(acc, self.visit(node.nodes[i]))
        return acc

    @visitor.when(regex_nodes.OrNode)
    def visit(self, node: regex_nodes.OrNode):
        acc = self.visit(node.children[0])
        for i in range(1, len(node.children)):
            acc = regex_operations_automata.join_nfas(acc, self.visit(node.children[i]))
        return acc

    @visitor.when(regex_nodes.KleeneNode)
    def visit(self, node: regex_nodes.KleeneNode):
        value = self.visit(node.child)
        return regex_operations_automata.kleene_closure(value)

    @visitor.when(regex_nodes.CharNode)
    def visit(self, node: regex_nodes.CharNode):
        return regex_operations_automata.build_basic_nfa(node.token)
