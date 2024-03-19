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
declarations, function_declaration, var_declaration, assignments, arg_list = G.NonTerminals(
    '<declarations> <func_declaration> <var_declaration> <assignments> <arg_list>')
destructive_assignment = G.NonTerminal("<destructive_ass>")

# Adding conditional NonTerminals
conditional, conditional_ending = G.NonTerminals('<conditional> <conditional_ending>')
inequality, equality = G.NonTerminals('<inequality> <equality>')

# Adding looping Non terminals
while_loop, for_loop = G.NonTerminals('<while> <for>')

# Adding basic terminals
obracket, cbracket, semicolon, opar, cpar, arrow, comma, colon = G.Terminals('{ } ; ( ) => , :')

# Adding declaration terminals
let, _in, _type, _id, equal, dest_eq = G.Terminals('let in <type> <id> = :=')

# Adding conditional terminals
_if, _else, _elif = G.Terminals('if else elif')

# Adding looping terminals
_while, _for = G.Terminals('while for')

# Adding function terminals
function = G.Terminal('function')

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
program %= expression
program %= declarations + expression

declarations %= declarations + function_declaration
declarations %= function_declaration

# An expression block is a sequence of expressions between brackets
expression_block %= obracket + expression_list + cbracket

expression_list %= expression + semicolon + expression_list
expression_list %= expression + semicolon
expression_list %= expression

# An expression is ...
# todo see https://github.com/matcom/hulk/blob/master/docs/guide/functions.md
expression %= expression_block
expression %= conditional
expression %= while_loop
expression %= for_loop
expression %= string_expression
expression %= destructive_assignment

# String expression
string_expression %= string_expression + amper + boolean_exp
string_expression %= string_expression + double_amp + boolean_exp
string_expression %= boolean_exp

# A boolean expression is a disjunction of conjunctive components,
boolean_exp %= boolean_exp + or_op + conjunctive_component
boolean_exp %= conjunctive_component

conjunctive_component %= conjunctive_component + and_op + neg
conjunctive_component %= neg

neg %= not_op + equality
neg %= equality

# todo makes sense 5 == 5 == 5 ?
equality %= inequality + eq + inequality
equality %= inequality + neq + inequality
equality %= inequality

# makes sense 3 <= 8 <= 11 ?
# No, book page 148
inequality %= arithmetic_exp + leq + arithmetic_exp
inequality %= arithmetic_exp + geq + arithmetic_exp
inequality %= arithmetic_exp + lt + arithmetic_exp
inequality %= arithmetic_exp + gt + arithmetic_exp
inequality %= arithmetic_exp

# An arithmetic expression is a sum or sub of terms,
# which is a multiplication/division of factors,
# which is a power of factors
arithmetic_exp %= arithmetic_exp + plus + term
arithmetic_exp %= arithmetic_exp + minus + term
arithmetic_exp %= term

term %= term + star + signed
term %= term + div + signed
term %= term + mod + signed
term %= signed

signed %= plus + powers
signed %= minus + powers
signed %= powers

powers %= factor + power + powers
powers %= factor + power2 + powers
powers %= factor

# todo any issue if factor and atom are merged ?

factor %= opar + expression + cpar
factor %= atom

atom %= number
atom %= bool_term
atom %= str_term
atom %= _id
atom %= func_call

func_call %= _id + opar + expr_list_comma_sep + cpar

expr_list_comma_sep %= expression
expr_list_comma_sep %= expression + comma + expression_list

# Var declarations:
var_declaration %= let + assignments + _in + expression

assignments %= assignments + comma + _id + equal + expression
assignments %= _id + equal + expression

# Destructive assigment
destructive_assignment %= _id + dest_eq + expression

# Functions can be declared using lambda notation or classic notation
function_declaration %= function + _id + opar + arg_list + cpar + arrow + expression
function_declaration %= function + _id + opar + arg_list + cpar + expression_block

arg_list %= arg_list + comma + _id
arg_list %= _id

# Conditional statements must have else
conditional %= _if + opar + expression + cpar + expression + conditional_ending

conditional_ending %= _elif + opar + expression + cpar + expression + conditional_ending
conditional_ending %= _else + expression

# Loop expression
while_loop %= _while + opar + expression + cpar + expression
for_loop %= _for + opar + expression + cpar + expression
