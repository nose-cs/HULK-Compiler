import src.hulk_grammar.hulk_ast_nodes as hulk_ast_nodes
from src.pycompiler import Grammar

G = Grammar()

# ----------------------------------------------NonTerminals---------------------------------------------------------- #

# Start symbol of the grammar
program = G.NonTerminal('<program>', startSymbol=True)

# Adding basic non-terminals
(expr_block, expr_list, expr_list_comma_sep, simple_expr, expr, eol_expr) = G.NonTerminals(
    '<expression_block> <expression_list> <expr_list_comma_sep> <simple_expression> <expression> <eol_expression>')

concat_operation, or_operation, and_operation, not_operation = G.NonTerminals(
    '<concat_operation> <or_operation> <and_operation> <not_operation>')

plus_or_minus_operation, star_div_or_mod_operation, pow_operation, sign_operation, factor, atom = G.NonTerminals(
    '<plus_or_minus_operation> <star_div_or_mod_operation> <pow_operation> <sign_operation> <factor> <atom>')

destructive_assignment, is_or_as_operation = G.NonTerminals("<destructive_ass> <is_or_as_operation>")

func_call, obj_method_or_attribute_call, type_instantiation = G.NonTerminals(
    '<func-call> <object_method_or_attribute_call> <type_instantiation>')

# Adding non-terminals to types, protocols and functions declaration
declarations, type_declaration, protocol_declaration, function_declaration = G.NonTerminals(
    '<declarations> <type_declaration> <protocol_declaration> <function_declaration>')

typed_params, typed_params_or_empty, protocol_body, optional_params_for_type, type_body, type_body_or_empty = G.NonTerminals(
    '<typed_params> <typed_params_or_empty> <protocol_body> <optional_params_for_type> <type_body> <type_body_or_empty>')

method_declaration, method_signature, attribute, optional_inheritance, params_list, params_list_or_empty = (
    G.NonTerminals('<method_declaration> <method_signature> <attribute> <inheritance> <params> <params_or_empty>'))

# Adding let in expression non-terminals
let_in, assignments = G.NonTerminals('<let_in> <assignments>')

# Adding conditional expression non-terminals
conditional, conditional_ending = G.NonTerminals('<conditional> <conditional_ending>')
inequality, equality = G.NonTerminals('<inequality> <equality>')

# Adding vector expression non-terminals
vector_initialization, expr_list_comma_sep_or_empty = G.NonTerminals(
    '<vector_initialization> <expr_list_comma_sep_or_empty>')

# Adding loop expression non-terminals
while_loop, for_loop = G.NonTerminals('<while_loop> <for_loop>')

# Adding non-terminals to optionally type
optional_typing_var, optional_typing_param, optional_typing_return = G.NonTerminals(
    '<optional_typing_var> <optional_typing_param> <optional_typing_return>')

# ----------------------------------------------Terminals------------------------------------------------------------- #

double_bar, o_square_bracket, c_square_bracket, obracket, cbracket = G.Terminals('|| [ ] { }')

semicolon, opar, cpar, arrow, comma, colon, dot = G.Terminals('; ( ) => , : .')

protocol, extends, word_type, inherits, idx = G.Terminals('protocol extends type inherits <id>')

new, is_, as_ = G.Terminals('new is as')

equal, dest_eq = G.Terminals('= :=')

if_, else_, elif_ = G.Terminals('if else elif')

let, in_, = G.Terminals('let in')

while_, for_ = G.Terminals('while for')

function = G.Terminal('function')

plus, minus, star, div, power, mod, power2, number_literal = G.Terminals('+ - * / ^ % ** <number>')

eq, neq, leq, geq, lt, gt = G.Terminals('== != <= >= < >')

and_op, or_op, not_op, bool_literal = G.Terminals('& | ! <bool>')

amper, double_amp, string_literal = G.Terminals('@ @@ <string>')

# -----------------------------------------------Productions---------------------------------------------------------- #

# A program is 0 or more functions, types or protocols declarations followed by a single expression
program %= eol_expr, lambda h, s: hulk_ast_nodes.ProgramNode([], s[1])
program %= declarations + eol_expr, lambda h, s: hulk_ast_nodes.ProgramNode(s[1], s[2])

declarations %= declarations + function_declaration, lambda h, s: s[1] + [s[2]]
declarations %= function_declaration, lambda h, s: [s[1]]
declarations %= declarations + type_declaration, lambda h, s: s[1] + [s[2]]
declarations %= type_declaration, lambda h, s: [s[1]]
declarations %= declarations + protocol_declaration, lambda h, s: s[1] + [s[2]]
declarations %= protocol_declaration, lambda h, s: [s[1]]

# An end of line expression is an expression followed by a semicolon or an expression block
eol_expr %= expr + semicolon, lambda h, s: s[1]
eol_expr %= expr_block, lambda h, s: s[1]

# An expression block is a sequence of expressions between brackets
expr_block %= obracket + expr_list + cbracket, lambda h, s: hulk_ast_nodes.ExpressionBlockNode(s[2])

expr_list %= eol_expr + expr_list, lambda h, s: [s[1]] + s[2]
expr_list %= eol_expr, lambda h, s: [s[1]]

# An expression is a simple expression or an expression block
expr %= expr_block, lambda h, s: s[1]
expr %= simple_expr, lambda h, s: s[1]

simple_expr %= conditional, lambda h, s: s[1]
simple_expr %= let_in, lambda h, s: s[1]
simple_expr %= while_loop, lambda h, s: s[1]
simple_expr %= for_loop, lambda h, s: s[1]
simple_expr %= destructive_assignment, lambda h, s: s[1]

destructive_assignment %= (obj_method_or_attribute_call + dest_eq + expr,
                           lambda h, s: hulk_ast_nodes.DestructiveAssignmentNode(s[1], s[3]))
destructive_assignment %= or_operation, lambda h, s: s[1]

or_operation %= or_operation + or_op + and_operation, lambda h, s: hulk_ast_nodes.OrNode(s[1], s[3])
or_operation %= and_operation, lambda h, s: s[1]

and_operation %= and_operation + and_op + equality, lambda h, s: hulk_ast_nodes.AndNode(s[1], s[3])
and_operation %= equality, lambda h, s: s[1]

# todo dejarlo pasar y que de error en el type checker
equality %= inequality + eq + inequality, lambda h, s: hulk_ast_nodes.EqualNode(s[1], s[3])
equality %= inequality + neq + inequality, lambda h, s: hulk_ast_nodes.NotEqualNode(s[1], s[3])
equality %= inequality, lambda h, s: s[1]

# makes sense 3 <= 8 <= 11 ?
# No, compilers book page 148
inequality %= (is_or_as_operation + leq + is_or_as_operation,
               lambda h, s: hulk_ast_nodes.LessOrEqualNode(s[1], s[3]))
inequality %= (is_or_as_operation + geq + is_or_as_operation,
               lambda h, s: hulk_ast_nodes.GreaterOrEqualNode(s[1], s[3]))
inequality %= (is_or_as_operation + lt + is_or_as_operation,
               lambda h, s: hulk_ast_nodes.LessThanNode(s[1], s[3]))
inequality %= (is_or_as_operation + gt + is_or_as_operation,
               lambda h, s: hulk_ast_nodes.GreaterThanNode(s[1], s[3]))
inequality %= is_or_as_operation, lambda h, s: s[1]

is_or_as_operation %= concat_operation + is_ + idx, lambda h, s: hulk_ast_nodes.IsNode(s[1], s[3])
is_or_as_operation %= concat_operation + as_ + idx, lambda h, s: hulk_ast_nodes.AsNode(s[1], s[3])
is_or_as_operation %= concat_operation, lambda h, s: s[1]

concat_operation %= (concat_operation + amper + plus_or_minus_operation,
                     lambda h, s: hulk_ast_nodes.ConcatNode(s[1], s[3]))
concat_operation %= (concat_operation + double_amp + plus_or_minus_operation,
                     lambda h, s: hulk_ast_nodes.ConcatNode(
                         hulk_ast_nodes.ConcatNode(s[1], hulk_ast_nodes.ConstantStringNode(" ")),
                         s[3]))
concat_operation %= plus_or_minus_operation, lambda h, s: s[1]

plus_or_minus_operation %= (plus_or_minus_operation + plus + star_div_or_mod_operation,
                            lambda h, s: hulk_ast_nodes.PlusNode(s[1], s[3]))
plus_or_minus_operation %= (plus_or_minus_operation + minus + star_div_or_mod_operation,
                            lambda h, s: hulk_ast_nodes.MinusNode(s[1], s[3]))
plus_or_minus_operation %= star_div_or_mod_operation, lambda h, s: s[1]

star_div_or_mod_operation %= (star_div_or_mod_operation + star + sign_operation,
                              lambda h, s: hulk_ast_nodes.StarNode(s[1], s[3]))
star_div_or_mod_operation %= (star_div_or_mod_operation + div + sign_operation,
                              lambda h, s: hulk_ast_nodes.DivNode(s[1], s[3]))
star_div_or_mod_operation %= (star_div_or_mod_operation + mod + sign_operation,
                              lambda h, s: hulk_ast_nodes.ModNode(s[1], s[3]))
star_div_or_mod_operation %= sign_operation, lambda h, s: s[1]

sign_operation %= plus + pow_operation, lambda h, s: s[2]
sign_operation %= minus + pow_operation, lambda h, s: hulk_ast_nodes.NegNode(s[2])
sign_operation %= pow_operation, lambda h, s: s[1]

pow_operation %= type_instantiation + power + pow_operation, lambda h, s: hulk_ast_nodes.PowNode(s[1], s[3])
pow_operation %= type_instantiation + power2 + pow_operation, lambda h, s: hulk_ast_nodes.PowNode(s[1], s[3])
pow_operation %= type_instantiation, lambda h, s: s[1]

type_instantiation %= (new + idx + opar + expr_list_comma_sep_or_empty + cpar,
                       lambda h, s: hulk_ast_nodes.TypeInstantiationNode(s[2], s[4]))
type_instantiation %= not_operation, lambda h, s: s[1]

not_operation %= not_op + obj_method_or_attribute_call, lambda h, s: hulk_ast_nodes.NotNode(s[2])
not_operation %= obj_method_or_attribute_call, lambda h, s: s[1]

obj_method_or_attribute_call %= (obj_method_or_attribute_call + dot + idx + opar + expr_list_comma_sep_or_empty + cpar,
                                 lambda h, s: hulk_ast_nodes.MethodCallNode(s[1], s[3], s[5]))
obj_method_or_attribute_call %= (obj_method_or_attribute_call + dot + idx,
                                 lambda h, s: hulk_ast_nodes.AttributeCallNode(s[1], s[3]))
obj_method_or_attribute_call %= factor, lambda h, s: s[1]

factor %= opar + expr + cpar, lambda h, s: s[2]
factor %= atom, lambda h, s: s[1]

atom %= number_literal, lambda h, s: hulk_ast_nodes.ConstantNumNode(s[1])
atom %= bool_literal, lambda h, s: hulk_ast_nodes.ConstantBoolNode(s[1])
atom %= string_literal, lambda h, s: hulk_ast_nodes.ConstantStringNode(s[1])
atom %= idx, lambda h, s: hulk_ast_nodes.VariableNode(s[1])
atom %= func_call, lambda h, s: s[1]
atom %= vector_initialization, lambda h, s: s[1]

# Function call
func_call %= idx + opar + expr_list_comma_sep_or_empty + cpar, lambda h, s: hulk_ast_nodes.FunctionCallNode(s[1], s[3])

expr_list_comma_sep_or_empty %= G.Epsilon, lambda h, s: []
expr_list_comma_sep_or_empty %= expr_list_comma_sep, lambda h, s: s[1]

expr_list_comma_sep %= expr, lambda h, s: [s[1]]
expr_list_comma_sep %= expr + comma + expr_list_comma_sep, lambda h, s: [s[1]] + s[3]

# Vector initialization
vector_initialization %= (o_square_bracket + expr_list_comma_sep_or_empty + c_square_bracket,
                          lambda h, s: hulk_ast_nodes.VectorInitializationNode(s[2]))
vector_initialization %= (o_square_bracket + expr + double_bar + idx + in_ + expr + c_square_bracket,
                          lambda h, s: hulk_ast_nodes.VectorComprehensionNode(s[2], s[4], s[6]))

# Let in expression
let_in %= let + assignments + in_ + expr, lambda h, s: hulk_ast_nodes.LetInNode(s[2], s[4])

assignments %= assignments + comma + optional_typing_var, lambda h, s: s[1] + [s[3]]
assignments %= optional_typing_var, lambda h, s: [s[1]]

optional_typing_var %= idx + equal + expr, lambda h, s: hulk_ast_nodes.VarDeclarationNode(s[1], s[3])
optional_typing_var %= (idx + colon + idx + equal + expr,
                        lambda h, s: hulk_ast_nodes.VarDeclarationNode(s[1], s[5], s[3]))

# Functions can be declared using lambda notation or classic notation
function_declaration %= (function + idx + opar + params_list_or_empty + cpar + arrow + simple_expr + semicolon,
                         lambda h, s: hulk_ast_nodes.FunctionDeclarationNode(s[2], s[4], s[7]))
function_declaration %= (function + idx + opar + params_list_or_empty + cpar + expr_block,
                         lambda h, s: hulk_ast_nodes.FunctionDeclarationNode(s[2], s[4], s[6]))
function_declaration %= (function + idx + opar + params_list_or_empty + cpar + expr_block + semicolon,
                         lambda h, s: hulk_ast_nodes.FunctionDeclarationNode(s[2], s[4], s[6]))

# specifying return type
function_declaration %= (
    function + idx + opar + params_list_or_empty + cpar + colon + idx + arrow + simple_expr + semicolon,
    lambda h, s: hulk_ast_nodes.FunctionDeclarationNode(s[2], s[4], s[10], s[7]))
function_declaration %= (function + idx + opar + params_list_or_empty + cpar + colon + idx + expr_block,
                         lambda h, s: hulk_ast_nodes.FunctionDeclarationNode(s[2], s[4], s[8], s[7]))
function_declaration %= (
    function + idx + opar + params_list_or_empty + cpar + colon + idx + expr_block + semicolon,
    lambda h, s: hulk_ast_nodes.FunctionDeclarationNode(s[2], s[4], s[8], s[7]))

params_list_or_empty %= params_list, lambda h, s: s[1]
params_list_or_empty %= G.Epsilon, lambda h, s: []

params_list %= optional_typing_param, lambda h, s: [s[1]]
params_list %= params_list + comma + optional_typing_param, lambda h, s: s[1] + [s[3]]

optional_typing_param %= idx, lambda h, s: (s[1], None)
optional_typing_param %= idx + colon + idx, lambda h, s: (s[1], s[3])

# Conditional expressions must have one if and one else and can 0 or more elifs
conditional %= (if_ + opar + expr + cpar + expr + conditional_ending + else_ + expr,
                lambda h, s: hulk_ast_nodes.ConditionalNode([(s[3], s[5])] + s[6], s[8]))
conditional_ending %= (elif_ + opar + expr + cpar + expr + conditional_ending,
                       lambda h, s: [(s[3], s[5])] + s[6])
conditional_ending %= G.Epsilon, lambda h, s: []

# Loop expression
while_loop %= while_ + opar + expr + cpar + expr, lambda h, s: hulk_ast_nodes.WhileNode(s[3], s[5])

for_loop %= (for_ + opar + idx + in_ + expr + cpar + expr,
             lambda h, s: hulk_ast_nodes.ForNode(s[3], s[5], s[7]))

# Type declaration
type_declaration %= (
    word_type + idx + optional_params_for_type + optional_inheritance + obracket + type_body_or_empty + cbracket,
    lambda h, s: hulk_ast_nodes.TypeDeclarationNode(s[2], s[3], s[6], s[4]))
type_declaration %= (
    word_type + idx + optional_params_for_type + inherits + idx + opar + expr_list_comma_sep_or_empty + cpar + obracket + type_body_or_empty + cbracket,
    lambda h, s: hulk_ast_nodes.TypeDeclarationNode(s[2], s[3], s[10], s[5], s[7]))

optional_inheritance %= inherits + idx, lambda h, s: s[2]
optional_inheritance %= G.Epsilon, lambda h, s: None

optional_params_for_type %= opar + params_list_or_empty + cpar, lambda h, s: s[2]
optional_params_for_type %= G.Epsilon, lambda h, s: []

type_body_or_empty %= G.Epsilon, lambda h, s: []
type_body_or_empty %= type_body, lambda h, s: s[1]

type_body %= type_body + attribute, lambda h, s: s[1] + [s[2]]
type_body %= type_body + method_declaration, lambda h, s: s[1] + [s[2]]
type_body %= attribute, lambda h, s: [s[1]]
type_body %= method_declaration, lambda h, s: [s[1]]

# Method declaration
method_declaration %= (idx + opar + params_list_or_empty + cpar + arrow + simple_expr + semicolon,
                       lambda h, s: hulk_ast_nodes.MethodDeclarationNode(s[1], s[3], s[6]))
method_declaration %= (idx + opar + params_list_or_empty + cpar + expr_block,
                       lambda h, s: hulk_ast_nodes.MethodDeclarationNode(s[1], s[3], s[5]))
method_declaration %= (idx + opar + params_list_or_empty + cpar + expr_block + semicolon,
                       lambda h, s: hulk_ast_nodes.MethodDeclarationNode(s[1], s[3], s[5]))

# specifying return type
method_declaration %= (idx + opar + params_list_or_empty + cpar + colon + idx + arrow + simple_expr + semicolon,
                       lambda h, s: hulk_ast_nodes.MethodDeclarationNode(s[1], s[3], s[8], s[6]))
method_declaration %= (idx + opar + params_list_or_empty + cpar + colon + idx + expr_block,
                       lambda h, s: hulk_ast_nodes.MethodDeclarationNode(s[1], s[3], s[7], s[6]))
method_declaration %= (idx + opar + params_list_or_empty + cpar + colon + idx + expr_block + semicolon,
                       lambda h, s: hulk_ast_nodes.MethodDeclarationNode(s[1], s[3], s[7], s[6]))

# Attribute declaration
attribute %= idx + equal + eol_expr, lambda h, s: hulk_ast_nodes.AttributeDeclarationNode(s[1], s[3])
attribute %= (idx + colon + idx + equal + eol_expr,
              lambda h, s: hulk_ast_nodes.AttributeDeclarationNode(s[1], s[5], s[3]))

# Protocol declaration
protocol_declaration %= (protocol + idx + obracket + protocol_body + cbracket,
                         lambda h, s: hulk_ast_nodes.ProtocolDeclarationNode(s[2], s[4], None))
protocol_declaration %= (protocol + idx + extends + idx + obracket + protocol_body + cbracket,
                         lambda h, s: hulk_ast_nodes.ProtocolDeclarationNode(s[2], s[6], s[4]))

protocol_body %= protocol_body + method_signature, lambda h, s: s[1] + [s[2]]
protocol_body %= method_signature, lambda h, s: [s[1]]

method_signature %= (idx + opar + typed_params_or_empty + cpar + colon + idx + semicolon,
                     lambda h, s: hulk_ast_nodes.MethodSignatureDeclarationNode(s[1], s[3], s[6]))

typed_params_or_empty %= typed_params, lambda h, s: s[1]
typed_params_or_empty %= G.Epsilon, lambda h, s: []

typed_params %= typed_params + comma + idx + colon + idx, lambda h, s: s[1] + [(s[3], s[5])]
typed_params %= idx + colon + idx, lambda h, s: [(s[1], s[3])]
