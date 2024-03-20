from src.parsing import SLR1Parser
from src.regex.regex_grammar import getRegexGrammar
from src.utils import Token
from src.regex.evaluation import evaluate_reverse_parse
from src.regex.build_automaton_visitor import AutomataBuilderVisitor

def get_regex_automaton(regex : str):
    G, star, bar, opar, cpar, char = getRegexGrammar()

    def getRegexTerminalToken(charrr, force_char):
        if not force_char:
            match charrr:
                case star.Name:
                    return star, Token(charrr, star)
                case bar.Name:
                    return bar, Token(charrr, bar)
                case opar.Name:
                    return opar, Token(charrr, opar)
                case cpar.Name:
                    return cpar, Token(charrr, cpar)
        return char, Token(charrr, char)

    parser = SLR1Parser(G)

    terminals = []
    tokens = []

    force_char = False

    for charrr in regex:
        if charrr != '\\' or force_char:
            terminal, token = getRegexTerminalToken(charrr, force_char)
            terminals.append(terminal)
            tokens.append(token)
            force_char = False
        else:
            force_char = True

    terminals.append(G.EOF)
    tokens.append(Token(G.EOF.Name, G.EOF))

    parse, operations = parser(terminals)

    visitor = AutomataBuilderVisitor()
    return visitor.visit(evaluate_reverse_parse(parse, operations, tokens))