import src.visitor as visitor
import src.hulk_grammar.hulk_ast_nodes as hulk_nodes
from src.semantics.types import Type
from src.semantics.utils import Context
from src.semantics.types import NumberType, StringType, BoolType

class CodeGenC(object):

    def __init__(self, context) -> None:
        self.index_var = 0
        self.context: Context = context

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(hulk_nodes.ProgramNode)
    def visit(self, node: hulk_nodes.ProgramNode):
        return self.visit(node.expression)

    @visitor.when(hulk_nodes.TypeInstantiationNode)
    def visit(self, node: hulk_nodes.TypeInstantiationNode):
        code = "create" + node.idx + " ("
        before = len(code)        

        classs = self.context.get_type(node.idx)
        args = node.args

        while classs is not None and classs.name != "Object":
            for i, param in enumerate(classs.get_params()[0]):
                classs.node.scope.children[0].find_variable(param).setNameC(self.visit(args[i])[0])

            for att in classs.attributes:
                code += self.visit(att.node.expr)[0] + ", "

            args = classs.node.parent_args
            classs = classs.parent

        if before != len(code):
            code = code[:-2]
        
        code += ")"

        return code, self.context.get_type(node.idx)

    @visitor.when(hulk_nodes.MethodDeclarationNode)
    def visit(self, node: hulk_nodes.MethodDeclarationNode):
        return self.visit(node.expr)

    @visitor.when(hulk_nodes.FunctionDeclarationNode)
    def visit(self, node: hulk_nodes.FunctionDeclarationNode):
        return self.visit(node.expr)

    @visitor.when(hulk_nodes.ExpressionBlockNode)
    def visit(self, node: hulk_nodes.ExpressionBlockNode):
        code = ""

        for expression in node.expressions:
            c, type = self.visit(expression)
            code += c + ";\n"

        return code, type
    
    @visitor.when(hulk_nodes.PlusNode)
    def visit(self, node: hulk_nodes.PlusNode):
        lc, ltype = self.visit(node.left)
        rc, rtype = self.visit(node.right)

        assert ltype.name == rtype.name
        return "numberSum(" + lc + ", " + rc + ")", ltype
    
    @visitor.when(hulk_nodes.MinusNode)
    def visit(self, node: hulk_nodes.MinusNode):
        lc, ltype = self.visit(node.left)
        rc, rtype = self.visit(node.right)

        assert ltype.name == rtype.name
        return "numberMinus(" + lc + ", " + rc + ")", ltype

    @visitor.when(hulk_nodes.StarNode)
    def visit(self, node: hulk_nodes.StarNode):
        lc, ltype = self.visit(node.left)
        rc, rtype = self.visit(node.right)

        assert ltype.name == rtype.name
        return "numberMultiply(" + lc + ", " + rc + ")", ltype

    @visitor.when(hulk_nodes.DivNode)
    def visit(self, node: hulk_nodes.DivNode):
        lc, ltype = self.visit(node.left)
        rc, rtype = self.visit(node.right)

        assert ltype.name == rtype.name
        return "numberDivision(" + lc + ", " + rc + ")", ltype

    @visitor.when(hulk_nodes.VariableNode)
    def visit(self, node: hulk_nodes.VariableNode):
        return node.scope.find_variable(node.lex).nameC, node.scope.find_variable(node.lex).type

    @visitor.when(hulk_nodes.VarDeclarationNode)
    def visit(self, node: hulk_nodes.VarDeclarationNode):
        var = "v" + str(self.index_var)
        self.index_var += 1
        
        node.scope.find_variable(node.id).setNameC(var)

        c, type = self.visit(node.expr)
        return "Object* " + var + " = " + c, type
        
    @visitor.when(hulk_nodes.ConstantNumNode)
    def visit(self, node: hulk_nodes.ConstantNumNode):
        return "createNumber(" + node.lex + ")", NumberType()

    @visitor.when(hulk_nodes.ConstantBoolNode)
    def visit(self, node: hulk_nodes.ConstantBoolNode):
        return "createBool(" + node.lex + ")", BoolType()

    @visitor.when(hulk_nodes.ConstantStringNode)
    def visit(self, node: hulk_nodes.ConstantStringNode):
        return "createString(" + node.lex + ")", StringType()
    
    @visitor.when(hulk_nodes.LetInNode)
    def visit(self, node: hulk_nodes.LetInNode):
        code = ""

        for var_declaration in node.var_declarations:
            code += self.visit(var_declaration)[0] + ";\n"

        c, type = self.visit(node.body)
        code += c

        return code, type
    
    @visitor.when(hulk_nodes.FunctionCallNode)
    def visit(self, node: hulk_nodes.FunctionCallNode):
        if node.idx != "print":
            code = "function_" + node.idx + "("

            for arg in node.args:
                code += self.visit(arg)[0] + ", "

            if len(node.args) > 0:
                code = code[:-2]

            code += ")"
        else:
            assert len(node.args) == 1
            c, type = self.visit(node.args[0])
            code = "print(" + c + ", " + "\"fun_" + type.name + "_toString\")"; 

        return code, self.context.functions[node.idx].return_type

    @visitor.when(hulk_nodes.AsNode)
    def visit(self, node: hulk_nodes.AsNode):
        return self.visit(node.expression)[0], self.context.get_type(node.ttype)
    
    @visitor.when(hulk_nodes.AttributeCallNode)
    def visit(self, node: hulk_nodes.AttributeCallNode):
        c, type = self.visit(node.obj)

        att_type = type.get_attribute(node.attribute).type
        return "getAttributeValue(" + c + ", \"" + type.name + "_" + node.attribute + "\")", att_type
    
    @visitor.when(hulk_nodes.MethodCallNode)
    def visit(self, node: hulk_nodes.MethodCallNode):
        obj, obj_type = self.visit(node.obj)

        code = "method_" + obj_type.name + "_" + node.method.name + "(" + obj

        for arg in node.args:
            code += ", " + self.visit(arg)[0]

        code += ")"

        return code, node.method.return_type