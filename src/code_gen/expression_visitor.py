import src.visitor as visitor
import src.hulk_grammar.hulk_ast_nodes as hulk_nodes
from src.semantics.types import Type
from src.semantics.utils import Context
from src.semantics.types import NumberType, StringType, BoolType

class CodeGenC(object):

    def __init__(self, context) -> None:
        self.index_var = 0
        self.context: Context = context
        
        self.blocks_defs = ""

        self.condition_blocks = ""
        self.index_condition_blocks = 0

        self.if_else_blocks = ""
        self.index_if_else_blocks = 0

        self.while_blocks = ""
        self.index_while_blocks = 0

    def getlinesindented(self, code: str, add_return=False, collect_last_exp=False):
        lines = ["   " + line for line in code.split('\n') if len(line.strip(' ')) > 0]
        
        if add_return:
            lines[-1] = "   return " + lines[-1][3:]
        
        if collect_last_exp:
            lines[-1] = "   return_obj = " + lines[-1][3:]

        return '\n'.join(lines)

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
                classs.node.scope.children[0].find_variable(param).setNameC(self.visit(args[i]))

            for att in classs.attributes:
                code += self.visit(att.node.expr) + ", "

            args = classs.node.parent_args
            classs = classs.parent

        if before != len(code):
            code = code[:-2]
        
        code += ")"

        return code

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
            code += self.visit(expression) + ";\n"

        return code
    
    @visitor.when(hulk_nodes.PlusNode)
    def visit(self, node: hulk_nodes.PlusNode):
        return "numberSum(" + self.visit(node.left) + ", " + self.visit(node.right) + ")"
    
    @visitor.when(hulk_nodes.MinusNode)
    def visit(self, node: hulk_nodes.MinusNode):
        return "numberMinus(" + self.visit(node.left) + ", " + self.visit(node.right) + ")"

    @visitor.when(hulk_nodes.StarNode)
    def visit(self, node: hulk_nodes.StarNode):
        return "numberMultiply(" + self.visit(node.left) + ", " + self.visit(node.right) + ")"

    @visitor.when(hulk_nodes.DivNode)
    def visit(self, node: hulk_nodes.DivNode):
        return "numberDivision(" + self.visit(node.left) + ", " + self.visit(node.right) + ")"

    @visitor.when(hulk_nodes.VariableNode)
    def visit(self, node: hulk_nodes.VariableNode):
        return node.scope.find_variable(node.lex).nameC

    @visitor.when(hulk_nodes.VarDeclarationNode)
    def visit(self, node: hulk_nodes.VarDeclarationNode):
        var = "v" + str(self.index_var)
        self.index_var += 1
        
        node.scope.find_variable(node.id).setNameC(var)

        return "Object* " + var + " = " + self.visit(node.expr)
        
    @visitor.when(hulk_nodes.ConstantNumNode)
    def visit(self, node: hulk_nodes.ConstantNumNode):
        return "createNumber(" + node.lex + ")"

    @visitor.when(hulk_nodes.ConstantBoolNode)
    def visit(self, node: hulk_nodes.ConstantBoolNode):
        return "createBool(" + node.lex + ")"

    @visitor.when(hulk_nodes.ConstantStringNode)
    def visit(self, node: hulk_nodes.ConstantStringNode):
        return "createString(" + node.lex + ")"
    
    @visitor.when(hulk_nodes.LetInNode)
    def visit(self, node: hulk_nodes.LetInNode):
        code = ""

        for var_declaration in node.var_declarations:
            code += self.visit(var_declaration) + ";\n"

        code += self.visit(node.body)

        return code
    
    @visitor.when(hulk_nodes.FunctionCallNode)
    def visit(self, node: hulk_nodes.FunctionCallNode):
        code = "function_" + node.idx + "("

        for arg in node.args:
            code += self.visit(arg) + ", "

        if len(node.args) > 0:
            code = code[:-2]

        code += ")"
       
        return code

    @visitor.when(hulk_nodes.AsNode)
    def visit(self, node: hulk_nodes.AsNode):
        return self.visit(node.expression)
    
    @visitor.when(hulk_nodes.AttributeCallNode)
    def visit(self, node: hulk_nodes.AttributeCallNode):
        obj = self.visit(node.obj)

        type = node.scope.find_variable(obj).type
        
        if type.name == "Self":
            type = type.referred_type

        return "getAttributeValue(" + obj + ", \"" + type.name + "_" + node.attribute + "\")"
    
    @visitor.when(hulk_nodes.MethodCallNode)
    def visit(self, node: hulk_nodes.MethodCallNode):
        obj = self.visit(node.obj)

        args = ','.join(["Object*" for i in range(len(node.args))])

        if len(args) > 0:
            args = ',' + args

        code = "((Object* (*)(Object*" + args + "))" + \
                "getMethodForCurrentType(" + obj + ", \"" + node.method + "\", 0)" + \
                ")(" + obj

        for arg in node.args:
            code += ", " + self.visit(arg)

        code += ")"

        return code
    
    @visitor.when(hulk_nodes.ConditionalNode)
    def visit(self, node: hulk_nodes.ConditionalNode):
        vars = node.scope.get_variables(True)

        params = "("

        for var in vars:
            params += var.nameC + ", "

        if len(vars) > 0:
            params = params[:-2]     

        params += ")"

        conditions_codes = []

        for condition in node.conditions:
            condition_code = "Object* condition" + str(self.index_condition_blocks) + "("
            index_condition = self.index_condition_blocks
            self.index_condition_blocks += 1

            for var in vars:
                condition_code += "Object* " + var.nameC + ", "

            if len(vars) > 0:
                condition_code = condition_code[:-2]

            condition_code += ")"
            self.blocks_defs += condition_code + ";\n\n"

            condition_code += " {\n"

            condition_code += self.getlinesindented(self.visit(condition), True) + ";\n}"

            self.condition_blocks += condition_code + "\n\n"
            conditions_codes.append("condition" + str(index_condition) + params)


        code = "Object* ifElseBlock" + str(self.index_if_else_blocks) + "("
        index = self.index_if_else_blocks
        self.index_if_else_blocks += 1

        for var in vars:
            code += "Object* " + var.nameC + ", "

        if len(vars) > 0:
            code = code[:-2]

        code += ")"

        self.blocks_defs += code + ";\n\n"

        code += " {\n"
        
        code += "   if(*((bool*)getAttributeValue(" + conditions_codes[0] + ", \"value\"))) {\n"

        code += self.getlinesindented(self.getlinesindented(self.visit(node.expressions[0]), True)) + ";\n   }\n"

        for i in range(1, len(node.conditions)):
            code += "   else if(*((bool*)getAttributeValue(" + conditions_codes[i] + ", \"value\"))) {\n"
            code += self.getlinesindented(self.getlinesindented(self.visit(node.expressions[i]), True)) + ";\n   }\n"

        code += "   else {\n"
        code += self.getlinesindented(self.getlinesindented(self.visit(node.default_expr), True)) + ";\n   }\n"

        code += "}"

        self.if_else_blocks += code + "\n\n"

        return "ifElseBlock" + str(index) + params

    @visitor.when(hulk_nodes.GreaterThanNode)
    def visit(self, node: hulk_nodes.GreaterThanNode):
        return "numberGreaterThan(" + self.visit(node.left) + ", " + self.visit(node.right) + ")"
    
    @visitor.when(hulk_nodes.GreaterOrEqualNode)
    def visit(self, node: hulk_nodes.GreaterOrEqualNode):
        return "numberGreaterOrEqualThan(" + self.visit(node.left) + ", " + self.visit(node.right) + ")"
    
    @visitor.when(hulk_nodes.EqualNode)
    def visit(self, node: hulk_nodes.EqualNode):
        left = self.visit(node.left)

        code = "((Object* (*)(Object*, Object*))" + \
                "getMethodForCurrentType(" + left + ", \"equals\", 0)" + \
                ")(" + left + ", " + self.visit(node.right) + ")"

        return code
    
    @visitor.when(hulk_nodes.NotEqualNode)
    def visit(self, node: hulk_nodes.NotEqualNode):
        left = self.visit(node.left)

        code = "invertBool(((Object* (*)(Object*, Object*))" + \
                "getMethodForCurrentType(" + left + ", \"equals\", 0)" + \
                ")(" + left + ", " + self.visit(node.right) + "))"

        return code
    
    @visitor.when(hulk_nodes.LessThanNode)
    def visit(self, node: hulk_nodes.LessThanNode):
        return "numberLessThan(" + self.visit(node.left) + ", " + self.visit(node.right) + ")"
    
    @visitor.when(hulk_nodes.LessOrEqualNode)
    def visit(self, node: hulk_nodes.LessOrEqualNode):
        return "numberLessOrEqualThan(" + self.visit(node.left) + ", " + self.visit(node.right) + ")"
    
    @visitor.when(hulk_nodes.WhileNode)
    def visit(self, node: hulk_nodes.WhileNode):
        vars = node.scope.get_variables(True)

        params = "("

        for var in vars:
            params += var.nameC + ", "

        if len(vars) > 0:
            params = params[:-2]     

        params += ")"

        condition_code = "Object* condition" + str(self.index_condition_blocks) + "("
        index_condition = self.index_condition_blocks
        self.index_condition_blocks += 1

        for var in vars:
            condition_code += "Object* " + var.nameC + ", "

        if len(vars) > 0:
            condition_code = condition_code[:-2]

        condition_code += ")"
        self.blocks_defs += condition_code + ";\n\n"

        condition_code += " {\n"

        condition_code += self.getlinesindented(self.visit(node.condition), True) + ";\n}"

        self.condition_blocks += condition_code + "\n\n"


        code = "Object* whileBlock" + str(self.index_while_blocks) + "("
        index = self.index_while_blocks
        self.index_while_blocks += 1

        for var in vars:
            code += "Object* " + var.nameC + ", "

        if len(vars) > 0:
            code = code[:-2]

        code += ")"

        self.blocks_defs += code + ";\n\n"

        code += " {\n"
        code += "   Object* return_obj = NULL;\n"

        code += "   while(*((bool*)getAttributeValue(condition" + str(index_condition) + params + ", \"value\"))) {\n"
        code += self.getlinesindented(self.getlinesindented(self.visit(node.expression), False, True)) + ";\n"
        code += "   }\n"

        code += "   return return_obj;\n}"

        self.while_blocks += code + "\n\n"

        return "whileBlock" + str(index) + params
    
    @visitor.when(hulk_nodes.DestructiveAssignmentNode)
    def visit(self, node: hulk_nodes.DestructiveAssignmentNode):
        return "replaceObject(" + self.visit(node.target) + ", " + self.visit(node.expr) + ")"