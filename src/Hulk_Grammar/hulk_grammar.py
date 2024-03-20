import hulk_ast_nodes
from src.pycompiler import Grammar

G = Grammar()

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
funcs, function_signature, args, protocol_definition, introducing_args, body, posible_body, type_declaration, declarations, function_declaration, var_declaration, assignments, arg_list, decs = G.NonTerminals(
    '<funcs> <function_signature> <args> <protocol_definition> <introducing_args> <body> <posible_body> <type declaration> <declarations> <func_declaration> <var_declaration> <assignments> <arg_list> <decs>')
destructive_assignment = G.NonTerminal("<destructive_ass>")

# Adding conditional NonTerminals
conditional, conditional_ending = G.NonTerminals('<conditional> <conditional_ending>')
inequality, equality = G.NonTerminals('<inequality> <equality>')

# Adding vector NonTerminals

vector_initialization, elements = G.NonTerminals('<vector_initialization> <elements>')

# Adding looping Non terminals
while_loop, for_loop = G.NonTerminals('<while> <for>')

# Adding basic terminals
double_bar, o_square_bracket, c_square_bracket, obracket, cbracket, semicolon, opar, cpar, arrow, comma, colon = G.Terminals(
    '|| [ ] { } ; ( ) => , :')

# Adding declaration terminals
protocol, extends, word_type, let, in_, inherits, type_, idx, equal, dest_eq = G.Terminals(
    'protocol extends let in inherits <type> <id> = :=')

# Adding conditional terminals
if_, else_, elif_ = G.Terminals('if else elif')

# Adding looping terminals
while_, for_ = G.Terminals('while for')

# Adding function terminals
print_, function = G.Terminals('print function')

# Adding arithmetic Terminals
plus, minus, star, div, power, mod, power2 = G.Terminals('+ - * / ^ % **')
number = G.Terminal('<number>')

eq, neq, leq, geq, lt, gt = G.Terminals('== != <= >= < >')

# Adding boolean operators terminals
and_op, or_op, not_op, bool_term = G.Terminals('& | ! <bool>')

# Adding string terminals
amper, double_amp, str_term = G.Terminals('@ @@ <string>')

# -------------------------------------------------------------------------------------------------------------------- #

# A program has the function declarations and then an expression or an expression block
program %= expression, lambda h, s: hulk_ast_nodes.ProgramNode([], [s[1]])
program %= declarations + expression, lambda h, s: hulk_ast_nodes.ProgramNode(s[1], [s[2]])

declarations %= declarations + function_declaration, lambda h, s: s[1] + [s[2]]
declarations %= function_declaration, lambda h, s: [s[1]]
declarations %= declarations + type_declaration, lambda h, s: s[1] + [s[2]]
declarations %= type_declaration, lambda h, s: [s[1]]
declarations %= declarations + protocol_definition, lambda h, s: s[1] + [s[2]]
declarations %= protocol_definition, lambda h, s: [s[1]]

# A type declaration can inherit, receive params or both

type_declaration %= word_type + idx + posible_body
type_declaration %= word_type + idx + opar + introducing_args + cpar + posible_body
type_declaration %= word_type + idx + inherits + idx + posible_body
type_declaration %= word_type + idx + inherits + idx + opar + introducing_args + cpar + posible_body

posible_body %= obracket + cbracket
posible_body %= obracket + body + cbracket

introducing_args %= idx
introducing_args %= introducing_args + comma + idx

body %= body + assignments
body %= body + function_declaration,
body %= assignments
body %= function_declaration

# An expression block is a sequence of expressions between brackets

expression_block %= obracket + expression_list + cbracket, lambda h, s: hulk_ast_nodes.ExpressionBlockNode(s[2])

expression_list %= expression + semicolon + expression_list, lambda h, s: [s[1]] + s[3]
expression_list %= expression + semicolon, lambda h, s: [s[1]]
expression_list %= expression, lambda h, s: [s[1]]

# An expression is ...
# todo see https://github.com/matcom/hulk/blob/master/docs/guide/functions.md
expression %= expression_block, lambda h, s: s[1]
expression %= conditional, lambda h, s: s[1]
expression %= while_loop, lambda h, s: s[1]
expression %= for_loop, lambda h, s: s[1]
expression %= string_expression, lambda h, s: s[1]
expression %= destructive_assignment, lambda h, s: s[1]
expression %= vector_initialization, lambda h, s: s[1]

# String expression
string_expression %= string_expression + amper + boolean_exp, lambda h, s: hulk_ast_nodes.ConcatNode(s[1], s[3])
string_expression %= (string_expression + double_amp + boolean_exp,
                      lambda h, s: hulk_ast_nodes.ConcatWithSpaceBetweenNode(s[1], s[3]))
string_expression %= boolean_exp, lambda h, s: s[1]

# A boolean expression is a disjunction of conjunctive components,
boolean_exp %= boolean_exp + or_op + conjunctive_component, lambda h, s: hulk_ast_nodes.OrNode(s[1], s[3])
boolean_exp %= conjunctive_component, lambda h, s: s[1]

conjunctive_component %= conjunctive_component + and_op + neg, lambda h, s: hulk_ast_nodes.AndNode(s[1], s[3])
conjunctive_component %= neg, lambda h, s: s[1]

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

func_call %= idx + opar + expr_list_comma_sep + cpar, lambda h, s: hulk_ast_nodes.CallNode(s[1], s[3])

expr_list_comma_sep %= expression, lambda h, s: [s[1]]
expr_list_comma_sep %= expression + comma + expression_list, lambda h, s: [s[1]] + s[3]

# Var declarations:
var_declaration %= let + assignments + in_ + expression, lambda h, s: hulk_ast_nodes.LetInNode(s[2], s[4])

assignments %= assignments + comma + idx + equal + expression, lambda h, s: s[1] + hulk_ast_nodes.VarDeclarationNode(
    s[3], s[5])
assignments %= idx + equal + expression, lambda h, s: hulk_ast_nodes.VarDeclarationNode(s[1], s[3])

# Destructive assigment
destructive_assignment %= idx + dest_eq + expression, lambda h, s: hulk_ast_nodes.DestructiveAssignmentNode(s[1], s[3])

# Functions can be declared using lambda notation or classic notation
function_declaration %= (function + idx + opar + arg_list + cpar + arrow + expression,
                         lambda h, s: hulk_ast_nodes.FunctionDeclarationNode(s[2], s[4], s[7]))
function_declaration %= (function + idx + opar + cpar + arrow + expression,
                         lambda h, s: hulk_ast_nodes.FunctionDeclarationNode(s[2], [], s[6]))
function_declaration %= (function + idx + opar + arg_list + cpar + expression_block,
                         lambda h, s: hulk_ast_nodes.FunctionDeclarationNode(s[2], s[4], s[6]))
function_declaration %= (function + idx + opar + cpar + expression_block,
                         lambda h, s: hulk_ast_nodes.FunctionDeclarationNode(s[2], [], s[5]))

arg_list %= arg_list + comma + idx, lambda h, s: s[1] + [s[3]]
arg_list %= idx, lambda h, s: [s[1]]

# Conditional statements must have else
conditional %= (if_ + opar + expression + cpar + expression + conditional_ending + else_ + expression,
                lambda h, s: hulk_ast_nodes.ConditionalNode([(s[3], s[5])] + s[6], s[8]))
conditional_ending %= (elif_ + opar + expression + cpar + expression + conditional_ending,
                       lambda h, s: [(s[3], s[5])] + s[6])
conditional_ending %= G.Epsilon, lambda h, s: []

# Loop expression
while_loop %= while_ + opar + expression + cpar + expression, lambda h, s: hulk_ast_nodes.WhileNode(s[3], s[5])

for_loop %= for_ + opar + idx + in_ + expression + cpar + expression, lambda h, s: hulk_ast_nodes.ForNode(s[3], s[5],
                                                                                                          s[7])

# Protocol declaration
protocol_definition %= protocol + idx + obracket + decs + cbracket
protocol_definition %= protocol + idx + extends + idx + obracket + decs + cbracket

decs %= decs + funcs
decs %= funcs
function_signature %= idx + opar + cpar + semicolon
function_signature %= idx + opar + args + cpar + semicolon
args %= args + idx + colon + type_
args %= idx + colon + type_

# Vector initialization
vector_initialization %= o_square_bracket + c_square_bracket
vector_initialization %= o_square_bracket + elements + c_square_bracket
vector_initialization %= o_square_bracket + expression + double_bar + idx + in_ + expression
elements %= elements + comma + expression
elements %= expression
