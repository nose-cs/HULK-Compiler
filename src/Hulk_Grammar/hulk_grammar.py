from src.pycompiler import Grammar

G = Grammar()

# Start symbol of the program
program = G.NonTerminal('<program>', startSymbol=True)

# Basic expression NonTerminals
expression_block, expression_list, expression = G.NonTerminals('<expression_block> <expression_list> <expression>')

# Adding arithmetic expressions symbols
arithmetic_exp, term, factor, signed, atom = G.NonTerminals('<arithmetic_exp> <term> <factor> <signed> <atom>')
number = G.Terminal('number')

# Adding boolean expressions symbols
boolean_exp, conjunctive_component, neg, boolean = G.NonTerminals(
    '<boolean_exp> <disjunctive_component> <neg> <boolean>')

# Declarations NonTerminals
declarations, function_declaration, var_declaration, assignments, arg_list = G.NonTerminals(
    '<decs> <f_dec> <v_dec> <assignments> <arg_list>')

# Adding conditional NonTerminals
conditional, conditional_ending = G.NonTerminals('<conditional> <conditional_ending>')

inequality, equality = G.NonTerminals('<inequality> <equality>')

# Adding looping Non terminals

while_loop = G.NonTerminal('<while>')
for_loop = G.NonTerminals('<for>')

# Adding basic terminals

obracket, cbracket, semicolon, opar, cpar, arrow, comma, colon = G.Terminals('{ } ; ( ) => , :')

# Adding declaration terminals

let, _in, _type, _id, equal = G.Terminals('let in <type> <id> =')

# Adding conditional terminals

_if, _else, _elif = G.Terminals('if else elif')

# Adding looping terminals

_while, _for = G.Terminals('while for')

# Adding function terminals

function = G.Terminals('function')

# Adding arithmetic Terminals

plus, minus, star, div, power, mod, power2 = G.Terminals('+ - * / ^ % **')

eq, neq, leq, geq, gt, lt = G.Terminals('== != <= >= < >')

# Adding boolean operators terminals
and_op, or_op, not_op, bool_term = G.Terminals('& | ! <bool>')


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
expression %= boolean_exp

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

signed %= plus + factor
signed %= minus + factor
signed %= factor

factor %= atom + power + factor
factor %= atom + power2 + factor
factor %= atom

# todo add function call to atom
atom %= opar + expression + cpar
atom %= number
atom %= bool_term

# Var declarations:
var_declaration %= let + assignments + _in + expression

assignments %= assignments + comma + _id + equal + expression
assignments %= _id + equal + expression

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
