from src.semantics.formatter_visitor import Formatter
from src.semantics.type_builder_visitor import TypeBuilder
from src.semantics.type_checker_visitor import TypeChecker
from src.semantics.type_collector_visitor import TypeCollector
from src.semantics.type_inferrer_visitor import TypeInferrer
from src.semantics.var_collector_visitor import VarCollector


def semantic_analysis_pipeline(ast, debug=False):
    if debug:
        formatter = Formatter()
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
        print('---------------- COLLECTING VARIABLES ------------------')
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
        print('---------------- INFERRING TYPES ------------------')
    type_inference = TypeInferrer(context, errors)
    type_inference.visit(ast)
    # Check if there are any inference errors and change the types to ErrorType if there are
    inference_errors = context.inference_errors() + scope.inference_errors()
    errors.extend(inference_errors)
    if debug:
        print('Errors: [')
        for error in errors:
            print('\t', error)
        print(']')
        print('Context:')
        print(context)
        print('Scope:')
        print(scope)
        print('---------------- CHECKING TYPES ------------------')
    type_checker = TypeChecker(context, errors)
    type_checker.visit(ast)
    if debug:
        print('Errors: [')
        for error in errors:
            print('\t', error)
        print(']')
        print('Context:')
        print(context)
        print('Scope:')
        print(scope)
    return ast, errors, context, scope
