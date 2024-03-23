import hulk_grammar.hulk_ast_nodes as hulk_nodes
class GlobalContext:
    
    def __init__(self) -> None:
        self.typesParents = {}
        self.typesArguments = {}
        self.functionsArguments = {}

    def define_type(self, type: hulk_nodes.TypeDeclarationNode):
        if type.idx in self.typesParents:
            return [f'The type {type.idx} is declared more than once']
        if type.parent is None:
            self.typesParents[type.idx] = 'object' #todo what I have to put here?
        else:
            self.typeParents[type.idx] = type.parent.idx
        self.typesArguments[type.idx] = len(type.args)
        return []

    def define_function(self, function: hulk_nodes.FunctionDeclarationNode):
        if function.id in self.functionsArguments:
            return [f'The function {function.id} is declared more than once']
        self.functionsArguments[function.id] = len(function.args)

    def define_protocol(self, protocol: hulk_nodes.ProtocolDeclaration):
        #Todo, I have not an exact idea of what to do here
        pass

