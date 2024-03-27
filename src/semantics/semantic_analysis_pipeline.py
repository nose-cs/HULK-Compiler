from src.semantics.semantic import Scope
from src.semantics.type_builder_visitor import TypeBuilder
from src.semantics.type_collector_visitor import TypeCollector
from src.semantics.var_collector_visitor import VarCollector


def semantic_analysis_pipeline(ast, debug=False):
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
        print('=============== VAR COLLECTOR ================')
    checker = VarCollector(context, errors)
    scope = Scope()
    checker.visit(ast, scope)
    if debug:
        print('Errors: [')
        for error in errors:
            print('\t', error)
        print(']')
        print('Scopes:')
        print(scope)
    return ast, errors, context, scope
