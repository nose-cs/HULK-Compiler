from src.semantics.formatter_visitor import FormatterVisitor
from src.semantics.type_builder_visitor import TypeBuilder
from src.semantics.type_collector_visitor import TypeCollector
from src.semantics.utils import Scope
from src.semantics.var_collector_visitor import VarCollector
from src.semantics.type_inferer import TypeInfer


def semantic_analysis_pipeline(ast, debug=False):
    if debug:
        formatter = FormatterVisitor()
        formatted_ast = formatter.visit(ast)
        print('===================== AST =====================')
        print(formatted_ast)
    if debug:
        print('============== COLLECTING TYPES ===============')
    errors = []
    collector = TypeCollector(errors)
    collector.visit(ast)
    context = collector.context
    if debug:
        print('Errors: [')
        for error in errors:
            print('\t', error)
        print(']')
        print('Context:')
        print(context)
        print('=============== BUILDING TYPES ================')
    builder = TypeBuilder(context, errors)
    builder.visit(ast)
    if debug:
        print('Errors: [')
        for error in errors:
            print('\t', error)
        print(']')
        print('Context:')
        print(context)
        print('=============== CHECKING TYPES ================')
        print('---------------- VAR COLLECTOR ------------------')
    var_collector = VarCollector(context, errors)
    scope = var_collector.visit(ast)
    if debug:
        print('Errors: [')
        for error in errors:
            print('\t', error)
        print(']')
        print('Context:')
        print(context)
        print('Scope:')
        print(scope)
        print('---------------- TYPE INFERENCE ------------------')
    # type_inference = TypeInfer(context, errors)
    # type_inference.visit(ast, scope)
    # if debug:
    #     print('Errors: [')
    #     for error in errors:
    #         print('\t', error)
    #     print(']')
    #     print('Context:')
    #     print(context)
    #     print('Scope:')
    #     print(scope)
    return ast, errors, context, scope
