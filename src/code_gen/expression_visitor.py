import src.hulk_grammar.hulk_ast_nodes as hulk_nodes
import src.visitor as visitor
from src.semantics.utils import Context


class CodeGenC(object):

    def __init__(self, context) -> None:
        self.index_var = 0
        self.context: Context = context

        self.blocks_defs = ""

        self.let_in_blocks = ""
        self.index_let_in_blocks = 0

        self.if_else_blocks = ""
        self.index_if_else_blocks = 0

        self.loop_blocks = ""
        self.index_loop_blocks = 0

        self.method_call_blocks = ""
        self.index_method_call_blocks = 0

        self.create_blocks = ""
        self.index_create_blocks = 0

        self.vector_comp = ""
        self.index_vector_comp = 0

        self.vector_selector = ""
        self.index_vector_selector = 0

    @staticmethod
    def get_lines_indented(code: str, add_return=False, collect_last_exp=False):
        lines = ["   " + line for line in code.split('\n') if len(line.strip(' ')) > 0]

        if add_return:
            lines[-1] = "   return " + lines[-1][3:] + ";"

        if collect_last_exp:
            lines[-1] = "   return_obj = " + lines[-1][3:] + ";"

        return '\n'.join(lines)

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(hulk_nodes.TypeInstantiationNode)
    def visit(self, node: hulk_nodes.TypeInstantiationNode):
        vars = node.scope.get_variables(True)

        params = "("

        for var in vars:
            params += var.nameC + ", "

        if len(vars) > 0:
            params = params[:-2]

        params += ")"

        create_block = "Object* createBlock" + str(self.index_create_blocks) + "("
        index = self.index_create_blocks
        self.index_create_blocks += 1

        for var in vars:
            create_block += "Object* " + var.nameC + ", "

        if len(vars) > 0:
            create_block = create_block[:-2]

        create_block += ")"

        self.blocks_defs += create_block + ";\n\n"

        create_block += " {\n"

        def_vars = ""

        code = "   return create" + node.idx + "("
        before = len(code)

        classs = self.context.get_type(node.idx)
        args = node.args

        while classs is not None and classs.name != "Object":
            for i, param in enumerate(classs.params_names):
                var = "v" + str(self.index_var)
                self.index_var += 1

                def_vars += "   Object* " + var + " = " + self.visit(args[i]) + ";\n"
                classs.node.scope.children[0].find_variable(param).setNameC(var)

            for att in classs.attributes:
                code += "copyObject(" + self.visit(att.node.expr) + "), "

            args = classs.node.parent_args
            classs = classs.parent

        if before != len(code):
            code = code[:-2]

        code += ");"

        create_block += def_vars + "\n" + code + "\n}"
        self.create_blocks += create_block + "\n\n"

        return "createBlock" + str(index) + params

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

        code = code[:-2]

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

    @visitor.when(hulk_nodes.PowNode)
    def visit(self, node: hulk_nodes.PowNode):
        return "numberPow(" + self.visit(node.left) + ", " + self.visit(node.right) + ")"

    @visitor.when(hulk_nodes.VariableNode)
    def visit(self, node: hulk_nodes.VariableNode):
        return node.scope.find_variable(node.lex).nameC

    @visitor.when(hulk_nodes.VarDeclarationNode)
    def visit(self, node: hulk_nodes.VarDeclarationNode):
        var = "v" + str(self.index_var)
        self.index_var += 1

        node.scope.find_variable(node.id).setNameC(var)

        return "Object* " + var + " = copyObject(" + self.visit(node.expr) + ");"

    @visitor.when(hulk_nodes.ConstantNumNode)
    def visit(self, node: hulk_nodes.ConstantNumNode):
        return "createNumber(" + node.lex + ")"

    @visitor.when(hulk_nodes.ConstantBoolNode)
    def visit(self, node: hulk_nodes.ConstantBoolNode):
        return "createBoolean(" + node.lex + ")"

    @visitor.when(hulk_nodes.ConstantStringNode)
    def visit(self, node: hulk_nodes.ConstantStringNode):
        return "createString(" + node.lex + ")"

    @visitor.when(hulk_nodes.LetInNode)
    def visit(self, node: hulk_nodes.LetInNode):
        vars = node.scope.get_variables(True)

        params = "("

        for var in vars:
            params += var.nameC + ", "

        if len(vars) > 0:
            params = params[:-2]

        params += ")"

        code = "Object* letInNode" + str(self.index_let_in_blocks) + "("
        index = self.index_let_in_blocks
        self.index_let_in_blocks += 1

        for var in vars:
            code += "Object* " + var.nameC + ", "

        if len(vars) > 0:
            code = code[:-2]

        code += ")"

        self.blocks_defs += code + ";\n\n"

        code += " {\n"

        for var_declaration in node.var_declarations:
            code += "   " + self.visit(var_declaration) + "\n"

        code += self.get_lines_indented(self.visit(node.body), True) + "\n"
        code += "}"

        self.let_in_blocks += code + "\n\n"

        return "letInNode" + str(index) + params

    @visitor.when(hulk_nodes.FunctionCallNode)
    def visit(self, node: hulk_nodes.FunctionCallNode):
        code = "function_" + node.idx + "("

        for arg in node.args:
            code += "copyObject(" + self.visit(arg) + "), "

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

        if isinstance(node.obj, hulk_nodes.VariableNode):
            code = "((Object* (*)(Object*" + args + "))" + \
                   "getMethodForCurrentType(" + obj + ", \"" + node.method + "\", NULL)" + \
                   ")(" + obj

            for arg in node.args:
                code += ", copyObject(" + self.visit(arg) + ")"

            code += ")"

            return code

        else:
            vars = node.scope.get_variables(True)

            params = "("

            for var in vars:
                params += var.nameC + ", "

            if len(vars) > 0:
                params = params[:-2]

            params += ")"

            code = "Object* methodCallBlock" + str(self.index_method_call_blocks) + "("
            index = self.index_method_call_blocks
            self.index_method_call_blocks += 1

            for var in vars:
                code += "Object* " + var.nameC + ", "

            if len(vars) > 0:
                code = code[:-2]

            code += ")"

            self.blocks_defs += code + ";\n\n"

            code += " {\n"

            code += "   Object* obj = " + obj + ";\n"
            code += "   return ((Object* (*)(Object*" + args + "))" + \
                    "getMethodForCurrentType(obj, \"" + node.method + "\", NULL)" + \
                    ")(obj"

            for arg in node.args:
                code += ", copyObject(" + self.visit(arg) + ")"

            code += ");\n}"

            self.method_call_blocks += code + "\n\n"

            return "methodCallBlock" + str(index) + params

    @visitor.when(hulk_nodes.ConditionalNode)
    def visit(self, node: hulk_nodes.ConditionalNode):
        vars = node.scope.get_variables(True)

        params = "("

        for var in vars:
            params += var.nameC + ", "

        if len(vars) > 0:
            params = params[:-2]

        params += ")"

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

        code += "   if(*((bool*)getAttributeValue(" + self.visit(node.conditions[0]) + ", \"value\"))) {\n"

        code += self.get_lines_indented(self.get_lines_indented(self.visit(node.expressions[0]), True)) + "\n   }\n"

        for i in range(1, len(node.conditions)):
            code += "   else if(*((bool*)getAttributeValue(" + self.visit(node.conditions[i]) + ", \"value\"))) {\n"
            code += self.get_lines_indented(self.get_lines_indented(self.visit(node.expressions[i]), True)) + "\n   }\n"

        code += "   else {\n"
        code += self.get_lines_indented(self.get_lines_indented(self.visit(node.default_expr), True)) + "\n   }\n"

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

        if isinstance(node.left, hulk_nodes.VariableNode):
            code = "((Object* (*)(Object*, Object*))" + \
                   "getMethodForCurrentType(" + left + ", \"equals\", NULL)" + \
                   ")(" + left + ", " + self.visit(node.right) + ")"

            return code

        else:
            vars = node.scope.get_variables(True)

            params = "("

            for var in vars:
                params += var.nameC + ", "

            if len(vars) > 0:
                params = params[:-2]

            params += ")"

            code = "Object* methodCallBlock" + str(self.index_method_call_blocks) + "("
            index = self.index_method_call_blocks
            self.index_method_call_blocks += 1

            for var in vars:
                code += "Object* " + var.nameC + ", "

            if len(vars) > 0:
                code = code[:-2]

            code += ")"

            self.blocks_defs += code + ";\n\n"

            code += " {\n"

            code += "   Object* obj = " + left + ";\n"
            code += "   return ((Object* (*)(Object*, Object*))" + \
                    "getMethodForCurrentType(obj, \"equals\", NULL)" + \
                    ")(obj, " + self.visit(node.right) + ");"

            code += "\n}"

            self.method_call_blocks += code + "\n\n"

            return "methodCallBlock" + str(index) + params

    @visitor.when(hulk_nodes.NotEqualNode)
    def visit(self, node: hulk_nodes.NotEqualNode):
        left = self.visit(node.left)

        if isinstance(node.left, hulk_nodes.VariableNode):
            code = "invertBoolean(((Object* (*)(Object*, Object*))" + \
                   "getMethodForCurrentType(" + left + ", \"equals\", NULL)" + \
                   ")(" + left + ", " + self.visit(node.right) + "))"

            return code

        else:
            vars = node.scope.get_variables(True)

            params = "("

            for var in vars:
                params += var.nameC + ", "

            if len(vars) > 0:
                params = params[:-2]

            params += ")"

            code = "Object* methodCallBlock" + str(self.index_method_call_blocks) + "("
            index = self.index_method_call_blocks
            self.index_method_call_blocks += 1

            for var in vars:
                code += "Object* " + var.nameC + ", "

            if len(vars) > 0:
                code = code[:-2]

            code += ")"

            self.blocks_defs += code + ";\n\n"

            code += " {\n"

            code += "   Object* obj = " + left + ";\n"
            code += "   return invertBoolean(((Object* (*)(Object*, Object*))" + \
                    "getMethodForCurrentType(obj, \"equals\", NULL)" + \
                    ")(obj, " + self.visit(node.right) + "));"

            code += "\n}"

            self.method_call_blocks += code + "\n\n"

            return "methodCallBlock" + str(index) + params

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

        code = "Object* loopBlock" + str(self.index_loop_blocks) + "("
        index = self.index_loop_blocks
        self.index_loop_blocks += 1

        for var in vars:
            code += "Object* " + var.nameC + ", "

        if len(vars) > 0:
            code = code[:-2]

        code += ")"

        self.blocks_defs += code + ";\n\n"

        code += " {\n"
        code += "   Object* return_obj = NULL;\n"

        code += "   while(*((bool*)getAttributeValue(" + self.visit(node.condition) + ", \"value\"))) {\n"
        code += self.get_lines_indented(self.get_lines_indented(self.visit(node.expression), False, True)) + "\n"
        code += "   }\n"

        code += "   return return_obj;\n}"

        self.loop_blocks += code + "\n\n"

        return "loopBlock" + str(index) + params

    @visitor.when(hulk_nodes.DestructiveAssignmentNode)
    def visit(self, node: hulk_nodes.DestructiveAssignmentNode):
        return "replaceObject(" + self.visit(node.target) + ", " + self.visit(node.expr) + ")"

    @visitor.when(hulk_nodes.ModNode)
    def visit(self, node: hulk_nodes.ModNode):
        return "numberMod(" + self.visit(node.left) + ", " + self.visit(node.right) + ")"

    @visitor.when(hulk_nodes.VectorInitializationNode)
    def visit(self, node: hulk_nodes.VectorInitializationNode):
        return "createVector(" + str(len(node.elements)) + ", " + ", ".join(
            [self.visit(element) for element in node.elements]) + ")"

    @visitor.when(hulk_nodes.VectorComprehensionNode)
    def visit(self, node: hulk_nodes.VectorComprehensionNode):
        var_iter = "v" + str(self.index_var)
        self.index_var += 1
        node.scope.children[0].find_variable(node.var).setNameC(var_iter)

        selector = "Object* selector" + str(self.index_vector_selector) + " ("
        index_selector = self.index_vector_selector
        self.index_vector_selector += 1

        vars = node.scope.get_variables(True)

        for var in vars:
            selector += "Object* " + var.nameC + ", "

        selector += "Object* " + var_iter

        selector += ")"

        self.blocks_defs += selector + ";\n\n"

        selector += " {\n"
        selector += self.get_lines_indented(self.visit(node.selector), True) + "\n}"

        self.vector_selector += selector + "\n\n"

        vector_comp = "Object* vectorComprehension" + str(self.index_vector_comp) + " ("
        index_vec = self.index_vector_comp
        self.index_vector_comp += 1

        for var in vars:
            vector_comp += "Object* " + var.nameC + ", "

        if len(vars) > 0:
            vector_comp = vector_comp[:-2]

        vector_comp += ")"

        self.blocks_defs += vector_comp + ";\n\n"

        vector_comp += " {\n"

        vector_comp += "   Object* vector = " + self.visit(node.iterable) + ";\n"
        vector_comp += "   Object** list = getAttributeValue(vector, \"list\");\n"
        vector_comp += "   int size = *(int*)getAttributeValue(vector, \"size\");\n\n"

        vector_comp += "   Object** new_list = malloc(size * sizeof(Object*));\n\n"

        vector_comp += "   for(int i = 0; i < size; i++) {\n"
        vector_comp += "      new_list[i] = selector" + str(index_selector)

        params = "("

        for var in vars:
            params += var.nameC + ", "

        vector_comp += params + "list[i]);\n"

        if len(vars) > 0:
            params = params[:-2]

        params += ")"

        vector_comp += "   }\n\n"
        vector_comp += "   return createVectorFromList(size, new_list);\n"
        vector_comp += "}"

        self.vector_comp += vector_comp + "\n\n"

        return "vectorComprehension" + str(index_vec) + params

    @visitor.when(hulk_nodes.IndexingNode)
    def visit(self, node: hulk_nodes.IndexingNode):
        return "getElementOfVector(" + self.visit(node.obj) + ", " + self.visit(node.index) + ")"

    @visitor.when(hulk_nodes.ForNode)
    def visit(self, node: hulk_nodes.ForNode):
        var_iter = "v" + str(self.index_var)
        self.index_var += 1
        node.scope.children[0].find_variable(node.var).setNameC(var_iter)

        vars = node.scope.get_variables(True)

        params = "("

        for var in vars:
            params += var.nameC + ", "

        if len(vars) > 0:
            params = params[:-2]

        params += ")"

        code = "Object* loopBlock" + str(self.index_loop_blocks) + "("
        index = self.index_loop_blocks
        self.index_loop_blocks += 1

        for var in vars:
            code += "Object* " + var.nameC + ", "

        if len(vars) > 0:
            code = code[:-2]

        code += ")"

        self.blocks_defs += code + ";\n\n"

        code += " {\n"
        code += "   Object* return_obj = NULL;\n"
        code += "   Object* " + var_iter + " = NULL;\n"
        code += "   Object* iterable = " + self.visit(node.iterable) + ";\n"
        code += "   Object*(*next)(Object*) = getMethodForCurrentType(iterable, \"next\", NULL);\n"
        code += "   Object*(*current)(Object*) = getMethodForCurrentType(iterable, \"current\", NULL);\n\n"

        code += "   while(*(bool*)getAttributeValue(next(iterable), \"value\")) {\n"
        code += "      " + var_iter + " = current(iterable);\n\n"
        code += self.get_lines_indented(self.get_lines_indented(self.visit(node.expression), False, True)) + "\n"
        code += "   }\n"

        code += "   return return_obj;\n}"

        self.loop_blocks += code + "\n\n"

        return "loopBlock" + str(index) + params

    @visitor.when(hulk_nodes.OrNode)
    def visit(self, node: hulk_nodes.OrNode):
        return "boolOr(" + self.visit(node.left) + ", " + self.visit(node.right) + ")"

    @visitor.when(hulk_nodes.AndNode)
    def visit(self, node: hulk_nodes.AndNode):
        return "boolAnd(" + self.visit(node.left) + ", " + self.visit(node.right) + ")"

    @visitor.when(hulk_nodes.ConcatNode)
    def visit(self, node: hulk_nodes.ConcatNode):
        return "stringConcat(" + self.visit(node.left) + ", " + self.visit(node.right) + ")"

    @visitor.when(hulk_nodes.BaseCallNode)
    def visit(self, node: hulk_nodes.BaseCallNode):
        code = "((Object* (*)(Object*"

        for i in range(len(node.args)):
            code += ", Object*"

        code += "))getMethodForCurrentType(self, \"" + node.method_name + "\", \"" + node.parent_type.name + "\"))(self"

        for arg in node.args:
            code += ", " + self.visit(arg)

        code += ")"

        return code

    @visitor.when(hulk_nodes.IsNode)
    def visit(self, node: hulk_nodes.IsNode):
        try:
            self.context.get_type(node.ttype)
            return "isType(" + self.visit(node.expression) + ", \"" + node.ttype + "\")"
        except:
            return "isProtocol(" + self.visit(node.expression) + ", \"" + node.ttype + "\")"
