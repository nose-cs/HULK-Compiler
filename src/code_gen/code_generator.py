from typing import Any
from src.lexer.hulk_lexer import HulkLexer
from src.hulk_grammar.hulk_grammar import G
from src.parsing import LR1Parser
from src.evaluation import evaluate_reverse_parse
from src.semantics.semantic_analysis_pipeline import semantic_analysis_pipeline
import src.hulk_grammar.hulk_ast_nodes as hulk_nodes

class CCodeGenerator:
    def __init__(self) -> None:
        self.lexer = HulkLexer(True)
        self.parser = LR1Parser(G)
        self.type_conforms_to_protocols = {}

    def __call__(self, hulk_code: str, debug=False) -> Any:
        tokens, errors = self.lexer(hulk_code)

        derivation, operations = self.parser([t.token_type for t in tokens])
        ast = evaluate_reverse_parse(derivation, operations, tokens)
        ast, errors, context, scope = semantic_analysis_pipeline(ast, debug)

        for ttype in context.types.values():
            self.type_conforms_to_protocols[ttype.name] = []

            for protocol in context.protocols.values():
                if ttype.conforms_to(protocol):
                    self.type_conforms_to_protocols[ttype.name].append(protocol)

        return self.generate(ast, context)

    def generate(self, ast, context):
        from src.code_gen.expression_visitor import CodeGenC

        def getlinesindented(code: str, add_return=False):
            lines = ["   " + line for line in code.split('\n') if len(line.strip(' ')) > 0]
            
            if add_return:
                lines[-1] = "   return " + lines[-1][3:] + ";"
            
            return '\n'.join(lines)
            

        codgen = CodeGenC(context)

        declarations = ""
        type_create = ""
        methods_code = ""
        functions_code = ""
        main = ""

        create_defs = {}
        method_defs = {}
        function_defs = []

        for type in context.types.values():
            if type.name not in ["Number", "Boolean", "String", "Object", "Range"]:
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

                declarations += create_def + ";\n"

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
                    declarations += method_def + ";\n"
                        
                declarations += "\n"

        for function in context.functions.values():
            if function.name not in ['print', 'sqrt', 'sin', 'cos', 'exp', 'log', 'rand', 'range', 'parse']:
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
                    declarations += function_def + ";\n"

        declarations += '\n'

        for type in context.types.values():
            if type.name not in ["Number", "Boolean", "String", "Object", "Range"]:
                type_create += create_defs[type.name][0] + " {\n"
                type_create += "   Object* obj = createObject();\n"

                type_create += "\n"
                for param in create_defs[type.name][1]:
                    type_create += "   addAttribute(obj, \"" + param + "\", " + param + ");\n"

                type_create += "\n"

                current = type
                index = 0
                while current is not None:
                    type_create += "   addAttribute(obj, \"parent_type" + str(index) + "\", \"" + current.name + "\");\n"

                    if current.name in method_defs:
                        for method in method_defs[current.name]:
                            type_create += "   addAttribute(obj, \"" + method[1] + "\", *" + method[1] + ");\n"

                    current = current.parent
                    index += 1
                
                type_create += "\n"
                index = 0
                for protocol in self.type_conforms_to_protocols[type.name]:
                    type_create += "   addAttribute(obj, \"conforms_protocol" + str(index) + "\", \"" + protocol.name + "\");\n"
                    index += 1

                type_create += "   return obj;\n"
                type_create += "}\n\n"

        for type in context.types.values():
            if type.name not in ["Number", "Boolean", "String", "Object", "Range"]:
                if type.name in method_defs:
                    for method_def, method_name, method in method_defs[type.name]:
                        methods_code += method_def + " {\n"
                        methods_code += getlinesindented(codgen.visit(method.node), True) + "\n"
                        methods_code += "}\n\n"
                
        for function_def, function_name, function in function_defs:
            functions_code += function_def + " {\n"
            functions_code += getlinesindented(codgen.visit(function.node), True) + "\n"
            functions_code += "}\n\n"

        main += "\nint main() {\n"
        main += "   srand(time(NULL));\n\n"

        main += getlinesindented(codgen.visit(ast.expression)) + ";"

        main += "\n   return 0; \n}"

        return declarations + type_create + codgen.blocks_defs + codgen.let_in_blocks + codgen.if_else_blocks + codgen.loop_blocks + codgen.method_call_blocks + codgen.create_blocks + codgen.vector_selector + codgen.vector_comp + methods_code + functions_code + main