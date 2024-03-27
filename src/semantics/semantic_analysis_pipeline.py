from src.semantics.formatter_visitor import FormatterVisitor
from src.semantics.type_builder_visitor import TypeBuilder
from src.semantics.type_checker_visitor import TypeChecker
from src.semantics.type_collector_visitor import TypeCollector
from src.semantics.utils import Scope


def semantic_analysis_pipeline(ast, debug=False):
    if debug:
        formatter = FormatterVisitor()
        formatted_ast = formatter.visit(ast)
        print('============== AST ===============')
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
    scope = Scope()
    exp_type = checker.visit(ast, scope)
    if debug:
        print('Errors: [')
        for error in errors:
            print('\t', error)
        print(']')
        print('Scope:')
        print(scope)
    return ast, errors, context, scope
