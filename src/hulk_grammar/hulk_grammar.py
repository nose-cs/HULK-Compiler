import src.hulk_grammar.hulk_ast_nodes as hulk_ast_nodes
from src.pycompiler import Grammar

G = Grammar()

# ----------------------------------------------NonTerminals---------------------------------------------------------- #

# Start symbol of the program
program = G.NonTerminal('<program>', startSymbol=True)

# Basic expression NonTerminals
expression_block, expression_list, expression = G.NonTerminals('<expression_block> <expression_list> <expression>')

func_call, expr_list_comma_sep = G.NonTerminals('<func-call> <expr-list>')

# Adding arithmetic expressions symbols
arithmetic_exp, term, powers, factor, signed, atom = G.NonTerminals(
    '<arithmetic_exp> <term> <powers> <factor> <signed> <atom>')

# Adding boolean expressions symbols
boolean_exp, conjunctive_component, neg, boolean = G.NonTerminals(
    '<boolean_exp> <disjunctive_component> <neg> <boolean>')

# Adding string expressions symbols
string_expression = G.NonTerminal('<str_expr>')

# Declarations NonTerminals
funcs, typed_params, typed_params_or_empty, protocol_definition, params_for_type, type_body = G.NonTerminals(
    '<funcs> <typed_params> <typed_params_or_empty> <protocol_definition> <params_for_type> <type_body>')

type_declaration, declarations, function_declaration, let_in, assignments, params_list, protocol_body = G.NonTerminals(
    '<type_declaration> <declarations> <function_declaration> <let_in> <assignments> <params_list> <protocol_body>')

method_declaration, method_signature, attribute, inheritance, params, type_instantiation, method_call, attribute_call = G.NonTerminals(
    '<method_declaration> <method_signature> <attribute> <inheritance> <params> <type_instantiation>, <method_call> <attribute_call>')

destructive_assignment, is_operation, as_operation = G.NonTerminals("<destructive_ass> <is_operation> <as_operation>")

# Adding conditional NonTerminals
conditional, conditional_ending = G.NonTerminals('<conditional> <conditional_ending>')
inequality, equality = G.NonTerminals('<inequality> <equality>')

# Adding vector NonTerminals

vector_initialization, expr_list_comma_sep_or_empty = G.NonTerminals(
    '<vector_initialization> <expr_list_comma_sep_or_empty>')

# Adding looping Non terminals
while_loop, for_loop = G.NonTerminals('<while> <for>')

optional_typing_var, optional_typing_param, optional_typing_return = G.NonTerminals(
    '<optional_typing_var> <optional_typing_param> <optional_typing_return>')

# ----------------------------------------------Terminals------------------------------------------------------------- #

# Adding basic terminals
double_bar, o_square_bracket, c_square_bracket, obracket, cbracket = G.Terminals('|| [ ] { }')

semicolon, opar, cpar, arrow, comma, colon, dot = G.Terminals('; ( ) => , : .')

# Adding declaration terminals
protocol, extends, word_type, inherits, idx, new, is_, as_ = G.Terminals(
    'protocol extends type inherits <id> new is as')

equal, dest_eq = G.Terminals('= :=')

# Adding conditional terminals
if_, else_, elif_ = G.Terminals('if else elif')

let, in_, = G.Terminals('let in')

# Adding looping terminals
while_, for_ = G.Terminals('while for')

# Adding function terminals
function = G.Terminal('function')

# Adding arithmetic Terminals
plus, minus, star, div, power, mod, power2, number = G.Terminals('+ - * / ^ % ** <number>')

eq, neq, leq, geq, lt, gt = G.Terminals('== != <= >= < >')

# Adding boolean operators terminals
and_op, or_op, not_op, bool_term = G.Terminals('& | ! <bool>')

# Adding string terminals
amper, double_amp, str_term = G.Terminals('@ @@ <string>')

# -----------------------------------------------Productions---------------------------------------------------------- #

# A program has the function declarations and then an expression or an expression block
program %= expression, lambda h, s: hulk_ast_nodes.ProgramNode([], s[1])
program %= declarations + expression, lambda h, s: hulk_ast_nodes.ProgramNode(s[1], s[2])

declarations %= declarations + function_declaration, lambda h, s: s[1] + [s[2]]
declarations %= function_declaration, lambda h, s: [s[1]]
declarations %= declarations + type_declaration, lambda h, s: s[1] + [s[2]]
declarations %= type_declaration, lambda h, s: [s[1]]
declarations %= declarations + protocol_definition, lambda h, s: s[1] + [s[2]]
declarations %= protocol_definition, lambda h, s: [s[1]]

# An expression block is a sequence of expressions between brackets

expression_block %= obracket + expression_list + cbracket, lambda h, s: hulk_ast_nodes.ExpressionBlockNode(s[2])

expression_list %= expression + semicolon + expression_list, lambda h, s: [s[1]] + s[3]
expression_list %= expression, lambda h, s: [s[1]]

# An expression is ...
# todo see https://github.com/matcom/hulk/blob/master/docs/guide/functions.md
expression %= expression_block, lambda h, s: s[1]
expression %= conditional, lambda h, s: s[1]
expression %= let_in, lambda h, s: s[1]
expression %= while_loop, lambda h, s: s[1]
expression %= for_loop, lambda h, s: s[1]
expression %= destructive_assignment, lambda h, s: s[1]
expression %= vector_initialization, lambda h, s: s[1]

# todo check type instantiation, is and as priority
expression %= type_instantiation, lambda h, s: s[1]
expression %= as_operation, lambda h, s: s[1]

as_operation %= string_expression + as_ + idx, lambda h, s: hulk_ast_nodes.AsNode(s[1], s[3])
as_operation %= string_expression, lambda h, s: s[1]

# String expression
string_expression %= string_expression + amper + boolean_exp, lambda h, s: hulk_ast_nodes.ConcatNode(s[1], s[3])

string_expression %= (string_expression + double_amp + boolean_exp,
                      lambda h, s: hulk_ast_nodes.ConcatNode(s[1], hulk_ast_nodes.ConstantStringNode(" ")
                                                             ).concat_with(s[3]))
string_expression %= boolean_exp, lambda h, s: s[1]

# A boolean expression is a disjunction of conjunctive components,
boolean_exp %= boolean_exp + or_op + conjunctive_component, lambda h, s: hulk_ast_nodes.OrNode(s[1], s[3])
boolean_exp %= conjunctive_component, lambda h, s: s[1]

conjunctive_component %= conjunctive_component + and_op + neg, lambda h, s: hulk_ast_nodes.AndNode(s[1], s[3])
conjunctive_component %= neg, lambda h, s: s[1]

is_operation %= neg + is_ + idx, lambda h, s: hulk_ast_nodes.IsNode(s[1], s[3])
is_operation %= neg, lambda h, s: s[1]

neg %= not_op + equality, lambda h, s: hulk_ast_nodes.NotNode(s[2])
neg %= equality, lambda h, s: s[1]

# todo makes sense 5 == 5 == 5 ?
equality %= inequality + eq + inequality, lambda h, s: hulk_ast_nodes.EqualNode(s[1], s[3])
equality %= inequality + neq + inequality, lambda h, s: hulk_ast_nodes.NotEqualNode(s[1], s[3])
equality %= inequality, lambda h, s: s[1]

# makes sense 3 <= 8 <= 11 ?
# No, book page 148
inequality %= arithmetic_exp + leq + arithmetic_exp, lambda h, s: hulk_ast_nodes.LessOrEqualNode(s[1], s[3])
inequality %= arithmetic_exp + geq + arithmetic_exp, lambda h, s: hulk_ast_nodes.GreaterOrEqualNode(s[1], s[3])
inequality %= arithmetic_exp + lt + arithmetic_exp, lambda h, s: hulk_ast_nodes.LessThanNode(s[1], s[3])
inequality %= arithmetic_exp + gt + arithmetic_exp, lambda h, s: hulk_ast_nodes.GreaterThanNode(s[1], s[3])
inequality %= arithmetic_exp, lambda h, s: s[1]

# An arithmetic expression is a sum or sub of terms,
# which is a multiplication/division of factors,
# which is a power of factors
arithmetic_exp %= arithmetic_exp + plus + term, lambda h, s: hulk_ast_nodes.PlusNode(s[1], s[3])
arithmetic_exp %= arithmetic_exp + minus + term, lambda h, s: hulk_ast_nodes.MinusNode(s[1], s[3])
arithmetic_exp %= term, lambda h, s: s[1]

term %= term + star + signed, lambda h, s: hulk_ast_nodes.StarNode(s[1], s[3])
term %= term + div + signed, lambda h, s: hulk_ast_nodes.DivNode(s[1], s[3])
term %= term + mod + signed, lambda h, s: hulk_ast_nodes.ModNode(s[1], s[3])
term %= signed, lambda h, s: s[1]

signed %= plus + powers, lambda h, s: s[2]
signed %= minus + powers, lambda h, s: hulk_ast_nodes.NegNode(s[2])
signed %= powers, lambda h, s: s[1]

powers %= factor + power + powers, lambda h, s: hulk_ast_nodes.PowNode(s[1], s[3])
powers %= factor + power2 + powers, lambda h, s: hulk_ast_nodes.PowNode(s[1], s[3])
powers %= factor, lambda h, s: s[1]

# todo any issue if factor and atom are merged ?

factor %= opar + expression + cpar, lambda h, s: s[2]
factor %= atom, lambda h, s: s[1]

atom %= number, lambda h, s: hulk_ast_nodes.ConstantNumNode(s[1])
atom %= bool_term, lambda h, s: hulk_ast_nodes.ConstantBoolNode(s[1])
atom %= str_term, lambda h, s: hulk_ast_nodes.ConstantStringNode(s[1])
atom %= idx, lambda h, s: hulk_ast_nodes.VariableNode(s[1])
atom %= func_call, lambda h, s: s[1]
atom %= method_call, lambda h, s: s[1]
atom %= attribute_call, lambda h, s: s[1]

func_call %= idx + opar + expr_list_comma_sep_or_empty + cpar, lambda h, s: hulk_ast_nodes.CallNode(s[1], s[3])

expr_list_comma_sep_or_empty %= G.Epsilon, lambda h, s: []
expr_list_comma_sep_or_empty %= expr_list_comma_sep, lambda h, s: s[1]

expr_list_comma_sep %= expression, lambda h, s: [s[1]]
expr_list_comma_sep %= expression + comma + expression_list, lambda h, s: [s[1]] + s[3]

# Var declarations:
let_in %= let + assignments + in_ + expression, lambda h, s: hulk_ast_nodes.LetInNode(s[2], s[4])

assignments %= assignments + comma + optional_typing_var, lambda h, s: s[1] + [s[3]]
assignments %= optional_typing_var, lambda h, s: [s[1]]

optional_typing_var %= idx + equal + expression, lambda h, s: hulk_ast_nodes.VarDeclarationNode(s[1], s[3])
optional_typing_var %= (idx + colon + idx + equal + expression,
                        lambda h, s: hulk_ast_nodes.VarDeclarationNode(s[1], s[5], s[3]))

# Destructive assigment
destructive_assignment %= idx + dest_eq + expression, lambda h, s: hulk_ast_nodes.DestructiveAssignmentNode(s[1], s[3])

# Functions can be declared using lambda notation or classic notation
function_declaration %= (function + idx + opar + params_list + cpar + arrow + expression + semicolon,
                         lambda h, s: hulk_ast_nodes.FunctionDeclarationNode(s[2], s[4], s[7]))
function_declaration %= (function + idx + opar + params_list + cpar + expression_block,
                         lambda h, s: hulk_ast_nodes.FunctionDeclarationNode(s[2], s[4], s[6]))
# specifying return type
function_declaration %= (function + idx + opar + params_list + cpar + colon + idx + arrow + expression + semicolon,
                         lambda h, s: hulk_ast_nodes.FunctionDeclarationNode(s[2], s[4], s[10], s[7]))
function_declaration %= (function + idx + opar + params_list + cpar + colon + idx + expression_block,
                         lambda h, s: hulk_ast_nodes.FunctionDeclarationNode(s[2], s[4], s[8], s[6]))

params_list %= params, lambda h, s: s[1]
params_list %= G.Epsilon, lambda h, s: []

params %= optional_typing_param, lambda h, s: [s[1]]
params %= params + comma + optional_typing_param, lambda h, s: s[1] + [s[3]]

# Conditional statements must have else
conditional %= (if_ + opar + expression + cpar + expression + conditional_ending + else_ + expression,
                lambda h, s: hulk_ast_nodes.ConditionalNode([(s[3], s[5])] + s[6], s[8]))
conditional_ending %= (elif_ + opar + expression + cpar + expression + conditional_ending,
                       lambda h, s: [(s[3], s[5])] + s[6])
conditional_ending %= G.Epsilon, lambda h, s: []

# Loop expression
while_loop %= while_ + opar + expression + cpar + expression, lambda h, s: hulk_ast_nodes.WhileNode(s[3], s[5])

for_loop %= (for_ + opar + idx + in_ + expression + cpar + expression,
             lambda h, s: hulk_ast_nodes.ForNode(s[3], s[5], s[7]))

# Type declaration
type_declaration %= (word_type + idx + params_for_type + inheritance + obracket + type_body + cbracket,
                     lambda h, s: hulk_ast_nodes.TypeDeclarationNode(s[2], s[3], s[6], s[4]))
type_declaration %= (
    word_type + idx + params_for_type + inherits + idx + opar + expr_list_comma_sep_or_empty + cpar + obracket + type_body + cbracket,
    lambda h, s: hulk_ast_nodes.TypeDeclarationNode(s[2], s[3], s[10], s[5], s[7]))

inheritance %= inherits + idx, lambda h, s: s[2]
inheritance %= G.Epsilon, lambda h, s: None

params_for_type %= opar + params_list + cpar, lambda h, s: s[2]
params_for_type %= G.Epsilon, lambda h, s: []

optional_typing_param %= idx, lambda h, s: hulk_ast_nodes.ParamNode(s[1])
optional_typing_param %= idx + colon + idx, lambda h, s: hulk_ast_nodes.ParamNode(s[1], s[3])

type_body %= type_body + attribute, lambda h, s: s[1] + [s[2]]
type_body %= type_body + method_declaration, lambda h, s: s[1] + [s[2]]
type_body %= attribute, lambda h, s: [s[1]]
type_body %= method_declaration, lambda h, s: [s[1]]

method_declaration %= (idx + opar + params_list + cpar + arrow + expression + semicolon,
                       lambda h, s: hulk_ast_nodes.MethodDeclarationNode(s[1], s[3], s[6]))
method_declaration %= (idx + opar + params_list + cpar + expression_block,
                       lambda h, s: hulk_ast_nodes.MethodDeclarationNode(s[1], s[3], s[5]))
# specifying return type
method_declaration %= (idx + opar + params_list + cpar + colon + idx + arrow + expression + semicolon,
                       lambda h, s: hulk_ast_nodes.MethodDeclarationNode(s[1], s[3], s[8], s[6]))
method_declaration %= (idx + opar + params_list + cpar + colon + idx + expression_block,
                       lambda h, s: hulk_ast_nodes.MethodDeclarationNode(s[1], s[3], s[7], s[5]))

attribute %= idx + equal + expression + semicolon, lambda h, s: hulk_ast_nodes.AttributeStatementNode(s[1], s[3])
attribute %= (idx + colon + idx + equal + expression + semicolon,
              lambda h, s: hulk_ast_nodes.AttributeStatementNode(s[1], s[5], s[3]))

# types instantiation
type_instantiation %= (new + idx + opar + expr_list_comma_sep_or_empty + cpar,
                       lambda h, s: hulk_ast_nodes.TypeInstantiationNode(s[2], s[4]))

method_call %= (idx + dot + idx + opar + expr_list_comma_sep_or_empty + cpar,
                lambda h, s: hulk_ast_nodes.MethodCallNode(s[1], s[3], s[5]))

attribute_call %= idx + dot + idx, lambda h, s: hulk_ast_nodes.AttributeCallNode(s[1], s[3])

# Protocol declaration
protocol_definition %= (protocol + idx + obracket + protocol_body + cbracket,
                        lambda h, s: hulk_ast_nodes.ProtocolDeclarationNode(s[2], s[4], None))
protocol_definition %= (protocol + idx + extends + idx + obracket + protocol_body + cbracket,
                        lambda h, s: hulk_ast_nodes.ProtocolDeclarationNode(s[2], s[6], s[4]))

protocol_body %= protocol_body + method_signature, lambda h, s: s[1] + [s[2]]
protocol_body %= method_signature, lambda h, s: [s[1]]

method_signature %= (idx + opar + typed_params_or_empty + cpar + colon + idx + semicolon,
                     lambda h, s: hulk_ast_nodes.MethodSignatureNode(s[1], s[3], s[6]))

typed_params_or_empty %= typed_params, lambda h, s: s[1]
typed_params_or_empty %= G.Epsilon, lambda h, s: []

typed_params %= typed_params + comma + idx + colon + idx, lambda h, s: s[1] + [hulk_ast_nodes.ParamNode(s[3], s[5])]
typed_params %= idx + colon + idx, lambda h, s: [hulk_ast_nodes.ParamNode(s[1], s[3])]

# Vector initialization
vector_initialization %= (o_square_bracket + expr_list_comma_sep_or_empty + c_square_bracket,
                          lambda h, s: hulk_ast_nodes.VectorInitializationNode(s[2]))
vector_initialization %= (o_square_bracket + expression + double_bar + idx + in_ + expression + c_square_bracket,
                          lambda h, s: hulk_ast_nodes.VectorComprehensionNode(s[2], s[4], s[6]))
