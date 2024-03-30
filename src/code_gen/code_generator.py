from typing import Any
from src.lexer.hulk_lexer import HulkLexer
from src.hulk_grammar.hulk_grammar import G
from src.parsing import LR1Parser
from src.evaluation import evaluate_reverse_parse
from src.semantics.semantic_analysis_pipeline import semantic_analysis_pipeline

class CCodeGenerator:
    def __init__(self) -> None:
        self.lexer = HulkLexer()
        self.parser = LR1Parser(G)

    def __call__(self, hulk_code: str) -> Any:
        tokens, errors = self.lexer(hulk_code)

        derivation, operations = self.parser([t.token_type for t in tokens])
        ast = evaluate_reverse_parse(derivation, operations, tokens)
        ast, errors, context, scope = semantic_analysis_pipeline(ast, debug=False)

        return self.generate(ast, context)

    def generate(self, ast, context):
        from src.code_gen.expression_visitor import CodeGenC

        def getlinesindented(code: str, add_return=False):
            lines = ["   " + line for line in code.split('\n') if len(line.strip(' ')) > 0]
            
            if add_return:
                lines[-1] = "   return " + lines[-1][3:]
            
            return '\n'.join(lines)
            

        codgen = CodeGenC(context)

        code = ""

        create_defs = {}
        method_defs = {}
        function_defs = []

        for type in context.types.values():
            if type.name not in ["Number", "Bool", "String", "Object"]:
                create_def = "Object* create" + type.name + " ("
                create_params = []

                current = type

                while current is not None:
                    for att in current.attributes:
                        create_params.append(current.name + "_" + att.name)
                        create_def += "Object* " + create_params[-1] + ", "

                    current = current.parent

                if len(create_params) > 0:
                    create_def = create_def[:-2]
                
                create_def += ")"

                create_defs[type.name] = (create_def, create_params)

                code += create_def + ";\n"

                method_defs[type.name] = []

                for method in type.methods:
                    method_name = "method_" + type.name + "_" + method.name
                    method_def = "Object* " + method_name + " (Object* self"
                    
                    method.node.scope.children[0].find_variable("self").setNameC("self")

                    for i, name in enumerate(method.param_names):
                        id_param = "p" + str(i)
                        method.node.scope.children[0].find_variable(name).setNameC(id_param)
                        method_def += ", Object* " + id_param

                    method_def += ")"
                    method_defs[type.name].append((method_def, method_name, method))
                    code += method_def + ";\n"
                        
                code += "\n"

        for function in context.functions.values():
            if function.name not in ['print', 'sqrt', 'sin', 'cos', 'exp', 'log', 'rand']:
                    function_name = "function_" + function.name
                    function_def = "Object* " + function_name + " ("
                    
                    for i, name in enumerate(function.param_names):
                        id_param = "p" + str(i)
                        function.node.scope.children[0].find_variable(name).setNameC(id_param)
                        function_def += "Object* " + id_param + ", "

                    if len(function.param_names):
                        function_def = function_def[:-2]

                    function_def += ")"
                    function_defs.append((function_def, function_name, function))
                    code += function_def + ";\n"

        code += '\n'

        for type in context.types.values():
            if type.name not in ["Number", "Bool", "String", "Object"]:
                code += create_defs[type.name][0] + " {\n"
                code += "   Object* obj = createObject();\n"

                code += "\n"
                for param in create_defs[type.name][1]:
                    code += "   addAttribute(obj, \"" + param + "\", " + param + ");\n"

                code += "\n"

                current = type
                index = 0
                while current is not None and current.name != "Object":
                    code += "   addAttribute(obj, \"parent_type" + str(index) + "\",\"" + current.name + "\");\n"

                    if current.name in method_defs:
                        for method in method_defs[current.name]:
                            code += "   addAttribute(obj, \"" + method[1] + "\", *" + method[1] + ");\n"

                    current = current.parent
                    index += 1
                
                code += "   return obj;\n"
                code += "}\n\n"

        for type in context.types.values():
            if type.name not in ["Number", "Bool", "String", "Object"]:
                if type.name in method_defs:
                    for method_def, method_name, method in method_defs[type.name]:
                        code += method_def + " {\n"
                        code += getlinesindented(codgen.visit(method.node)[0], True) + ";\n"
                        code += "}\n\n"
                
        for function_def, function_name, function in function_defs:
            code += function_def + " {\n"
            code += getlinesindented(codgen.visit(function.node)[0], True) + "\n"
            code += "}\n\n"

        code += "\nint main() {\n"

        code += getlinesindented(codgen.visit(ast.expression)[0]) + ";\n"

        code += "   return 0; \n}"

        return code