import src.hulk_grammar.hulk_ast_nodes as hulk_nodes
import src.visitor as visitor


def visit(node: hulk_nodes.ProgramNode):
    types = {}
    for decl in node.declarations:
        if(decl is hulk_nodes.TypeDeclarationNode):
            types[decl.idx] = len(decl)

