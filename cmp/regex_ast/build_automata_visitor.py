import visitor
import regex_nodes
import regex_operations_automata

class AutomataBuilderVisitor(object):
    @visitor.on('node')
    def visit(self, node, scope):
        pass

    @visitor.when(regex_nodes.RegexNode)
    def visit(self, node):
        acum = node.nodes[0]
        for i in range(1, len(self.nodes)):
            acum = regex_operations_automata.concatenate_nfas(acum, self.nodes[i])
        return acum
    
    @visitor.when(regex_nodes.OrNode)
    def visit(self, node):
        lvalue = node.left.evaluate()
        rvalue = node.right.evaluate()
        return regex_operations_automata.join_nfas(lvalue, rvalue)
    
    @visitor.when(regex_nodes.KleeneNode)
    def visit(self, node):
        value = node.child.evaluate()
        return regex_operations_automata.kleene_closure(value)
    
    @visit.when(regex_nodes.CharNode)
    def visit(self, node):
        return regex_operations_automata.build_basic_nfa(node.token)
        