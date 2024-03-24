import hulk_grammar.hulk_ast_nodes as hulk_nodes
from type import Type
from function import Function

class GlobalContext:
    
    def __init__(self) -> None:
        self.types = {}
        self.functions = {}
        self.methods = {}
        
    def define_type(self, type: hulk_nodes.TypeDeclarationNode):
        if type.idx in self.types:
            return [f'The type {type.idx} is declared more than once']
        self.types[type.idx] = Type(type.idx)
        if not type.parent: self.types[type.idx].parent = 'Object'
        return []

    def define_function(self, function: hulk_nodes.FunctionDeclarationNode):
        if function.id in self.functions:
            return [f'The function {function.id} is declared more than once']
        self.functions[function.id] = Function(function.id)

    def define_protocol(self, protocol: hulk_nodes.ProtocolDeclaration):
        #Todo, I have not an exact idea of what to do here
        pass





