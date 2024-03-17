from pycompiler import Grammar

G = Grammar()

#Start symbol of the program
program = G.NonTerminal('<program>', startSymbol = True)

#Basic expression NonTerminals
expresion_block, expresion_list, expresion = G.NonTerminals('<expresion_block> <expresion_list> <expresion>')


#Adding aritmetic expressions symbols
aritmetic_exp , term, factor, powers = G.NonTerminals('<aritmetic_exp> <term> <factor> <powers>')
number = G.Terminal('number')

#Adding boolean expressions symbols

boolean_exp, conjuntive_component, neg, boolean = G.NonTerminals('<boolean_exp> <disjunctive_component> <neg> <boolean>')

#Declarations NonTerminals
declarations, function_declaration , var_declaration , asigments , arg_list = G.NonTerminals('<decs> <f_dec> <v_dec> <assigments> <arg_list>')


#Adding condicional NonTerminals
conditional, conditional_ending = G.NonTerminals('<conditional> <conditional_ending>')

#Adding looping Nonterminals

while_loop = G.NonTerminal('<while>')

#Adding basic terminals

obracket , cbracket, semicolon, opar, cpar, arrow, comma = G.Terminals('{ } ; ( ) => ,')

#Adding declaration terminals

let, _type, _in, _id, equal = G.Terminals('let in <type> <id> =')

#Adding conditional terminals

_if, _else, _elif = G.Terminals('if else elif')

#Adding looping terminals

_while, _for = G.Terminals('while for')

#Adding aritmetic Terminals

plus, minus, star, div, power = G.Terminals('+ - * / ^') 

#Adding boolean operators terminals

and_op, or_op, not_op, bool_term = G.Terminals('& | ! <bool>')

#A program has the function declarations and then an expresion or an expression block

program %= expresion

program %= declarations + expresion

declarations %= declarations + function_declaration

declarations %= function_declaration


#An expresion block is a sequence of expresions between brackets

expresion_block %= obracket + expresion_list + cbracket

expresion_list %= expresion + semicolon + expresion_list

expresion_list %= expresion

#An expresion can be an aritmetic expresion, a boolean expresion, a loop, a conditional or an expresion block

expresion %= expresion_block

expresion %= aritmetic_exp

expresion %= boolean_exp

expresion %= conditional

expresion %= while_loop

#An aritmetic expresion is a sum/substraction of terms, which is a multiplication/division of powers, wich is a power of factors

aritmetic_exp %= aritmetic_exp + plus + term

aritmetic_exp %= aritmetic_exp + minus + term

aritmetic_exp %= term

term %= term + star + factor

term %= term + div + factor

term %= factor

factor %= powers + power + factor

factor %= powers + star + star + factor

factor %= powers

powers %= opar + expresion + cpar

powers %= number

#Var declarations:

var_declaration %= let + asigments + _in + expresion

asigments %= asigments + comma + _id + equal + expresion

asigments %= _id + equal + expresion

#A boolean expresion is a conjuntion of disjunctive components, wich are a disjunction of terms, wich are negated atoms or atoms. Atoms are booleans or expresions 

boolean_exp %= boolean_exp + or_op + conjuntive_component

boolean_exp %= conjuntive_component

conjuntive_component %= conjuntive_component + and_op + neg

conjuntive_component %= neg

neg %= not_op + neg

neg %= bool_term

boolean %= opar + expresion + cpar

boolean %= bool_term 

#Functions can be declarated using lambda notation or clasical notation

function_declaration %= _type + _id + opar + arg_list + cpar + arrow + expresion

function_declaration %= _type + _id + opar + arg_list + cpar + expresion_block

arg_list %= arg_list + comma + _type + _id

arg_list %= _type + _id

#Conditional statements must have else

conditional %= _if + opar + expresion + cpar + expresion + conditional_ending

conditional_ending %= _else + expresion

conditional_ending %= _elif + opar + expresion + cpar + expresion + conditional_ending

#Loop expresion 

while_loop %= _while + expresion + expresion

