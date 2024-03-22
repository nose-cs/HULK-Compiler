from src.pycompiler import Grammar
from src.regex import regex_nodes


def get_regex_grammar():
    G = Grammar()

    origin = G.NonTerminal('<origin>', startSymbol=True)

    regex = G.NonTerminal('<regex>')

    disjunction, kleene, factor = G.NonTerminals('<disjunction> <kleene> <factor>')

    star, bar, opar, cpar = G.Terminals('* | ( )')

    char = G.Terminal('char')

    origin %= regex, lambda _, s: regex_nodes.RegexNode(s[1])

    regex %= regex + disjunction, lambda _, s: s[1] + [regex_nodes.OrNode(s[2])]

    regex %= disjunction, lambda _, s: [regex_nodes.OrNode(s[1])]

    disjunction %= disjunction + bar + kleene, lambda _, s: s[1] + [s[3]]

    disjunction %= kleene, lambda _, s: [s[1]]

    kleene %= kleene + star, lambda _, s: regex_nodes.KleeneNode(s[1])

    kleene %= factor, lambda _, s: s[1]

    factor %= opar + regex + cpar, lambda _, s: regex_nodes.RegexNode(s[2])

    factor %= char, lambda _, s: regex_nodes.CharNode(s[1])

    return G, star, bar, opar, cpar, char
