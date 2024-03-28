from src.semantics.formatter_visitor import FormatterVisitor
from src.semantics.type_builder_visitor import TypeBuilder
from src.semantics.type_checker_visitor import TypeChecker
from src.semantics.type_collector_visitor import TypeCollector


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
    checker = TypeChecker(context, errors)
    scope = checker.visit(ast)
    if debug:
        print('Errors: [')
        for error in errors:
            print('\t', error)
        print(']')
        print('Context:')
        print(context)
        print('Scope:')
        print(scope)
        if scope.there_is_auto_type_in_scope():
            print('There is an auto type in the scope')
    return ast, errors, context, scope
