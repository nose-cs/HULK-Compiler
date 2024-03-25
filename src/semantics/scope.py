class Scope:
    def __init__(self, parent = None, declarated_vars = {}) -> None:
        self.local_vars = declarated_vars
        self.parent:Scope = parent

    def newContext(self, varset):
        return Scope(self, varset)
    
    def isDefined(self, var):
        if var in self.local_vars: return True
        else: return False if self.parent is None else self.parent.IsDefined(var)

    def define(self, var):
        self.local_vars.add(var)