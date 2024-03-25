from src.pycompiler import Grammar
from src.regex import regex_nodes


def get_regex_grammar():
    G = Grammar()

    origin = G.NonTerminal('<origin>', startSymbol=True)

    disjunction = G.NonTerminal('<disjunction>')

    concat, kleene, factor = G.NonTerminals('<concat> <kleene> <factor>')

    star, bar, opar, cpar = G.Terminals('* | ( )')

    char = G.Terminal('char')

    origin %= disjunction, lambda _, s: regex_nodes.OrNode(s[1])

    disjunction %= disjunction + bar + concat, lambda _, s: s[1] + [regex_nodes.ConcatNode(s[3])]

    disjunction %= concat, lambda _, s: [regex_nodes.ConcatNode(s[1])]

    concat %= concat + kleene, lambda _, s: s[1] + [s[2]]

    concat %= kleene, lambda _, s: [s[1]]

    kleene %= kleene + star, lambda _, s: regex_nodes.KleeneNode(s[1])

    kleene %= factor, lambda _, s: s[1]

    factor %= opar + disjunction + cpar, lambda _, s: regex_nodes.OrNode(s[2])

    factor %= char, lambda _, s: regex_nodes.CharNode(s[1])

    return G, star, bar, opar, cpar, char
