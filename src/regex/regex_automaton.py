from src.evaluation import evaluate_reverse_parse
from src.parsing import SLR1Parser
from src.regex.build_automaton_visitor import AutomataBuilderVisitor
from src.regex.regex_grammar import get_regex_grammar
from src.utils import Token


def get_regex_automaton(regex: str):
    G, star, bar, opar, cpar, char = get_regex_grammar()

    def get_regex_terminal_token(charrr, force_char):
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
            terminal, token = get_regex_terminal_token(charrr, force_char)
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
