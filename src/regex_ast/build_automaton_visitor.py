import regex_nodes
import src.automaton_operations as regex_operations_automata
import src.visitor as visitor


class AutomataBuilderVisitor(object):
    @visitor.on('node')
    def visit(self, node: regex_nodes.Node, scope):
        pass

    @visitor.when(regex_nodes.RegexNode)
    def visit(self, node: regex_nodes.RegexNode):
        acc = node.nodes[0]
        for i in range(1, len(node.nodes)):
            acc = regex_operations_automata.concatenate_nfas(acc, node.nodes[i])
        return acc

    @visitor.when(regex_nodes.OrNode)
    def visit(self, node):
        lvalue = self.visit(node.left)
        rvalue = self.visit(node.right)
        return regex_operations_automata.join_nfas(lvalue, rvalue)

    @visitor.when(regex_nodes.KleeneNode)
    def visit(self, node):
        value = self.visit(node.child)
        return regex_operations_automata.kleene_closure(value)

    @visit.when(regex_nodes.CharNode)
    def visit(self, node):
        return regex_operations_automata.build_basic_nfa(node.token)
