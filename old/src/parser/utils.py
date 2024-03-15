import sys
sys.path.insert(1, '..')

from automaton.nfa import NFA, NFAState
from automaton.dfa import DFA

EPSILON = 'ε'

def calculate_first(productions, terminals, non_terminals):
    first_sets = {symbol: (set() if symbol in non_terminals else {symbol}) for symbol in terminals | non_terminals}
    changed = True

    while changed:
        changed = False
        for nt in non_terminals:
            for production in productions.get(nt, []):
                for symbol in production:
                    before_update = len(first_sets[nt])
                    if symbol in terminals:
                        first_sets[nt].add(symbol)

                        if len(first_sets[nt]) > before_update:
                            changed = True

                        break
                    elif symbol != 'ε':
                        first_sets[nt] |= (first_sets[symbol] - {'ε'})

                        if len(first_sets[nt]) > before_update:
                            changed = True

                        if 'ε' not in first_sets[symbol]:
                            break
                else:
                    first_sets[nt].add('ε')
    return first_sets

def calculate_follow(productions, terminals, non_terminals, start_symbol):
    first_sets = calculate_first(productions, terminals, non_terminals)
    follow_sets = {nt: set() for nt in non_terminals}
    follow_sets[start_symbol].add('$')

    changed = True
    while changed:
        changed = False
        for nt in non_terminals:
            for production in productions.get(nt, []):
                for i, symbol in enumerate(production):
                    if symbol in non_terminals:
                        before_update = len(follow_sets[symbol])
                        
                        if i + 1 < len(production):
                            next_symbol = production[i + 1]
                            follow_sets[symbol] |= (first_sets[next_symbol] - {'ε'})
                            
                            j = 2
                            while i + j <= len(production):
                                if i + j == len(production):
                                    if 'ε' in first_sets[next_symbol]:
                                        follow_sets[symbol] |= follow_sets[nt]
                                    break
                                elif 'ε' in first_sets[next_symbol]:
                                    next_symbol = production[i + j]
                                    follow_sets[symbol] |= (first_sets[next_symbol] - {'ε'})
                                    j += 1
                                else:
                                    break
                            
                        else:
                            follow_sets[symbol] |= follow_sets[nt]
                        
                        if len(follow_sets[symbol]) > before_update:
                            changed = True
    return follow_sets

def createAutomatonSLR1(productions: dict, non_terminals, start_symbol):
    aum = NFAState(0)
    aum1 = NFAState(1, True) 
    aum1.properties['final'] = ('SS', 0)

    aum.add_transition(start_symbol, aum1)

    nodes = {'SS': [[aum, aum1]]}

    index = 2
    for head, body in productions.items():
        nodes[head] = []
        
        for p, production in enumerate(body):
            inicial = NFAState(index)

            nodes[head].append([inicial])

            current = inicial

            for i, token in enumerate(production):
                index += 1

                new = NFAState(index, i + 1 == len(production))

                if i + 1 == len(production):
                    new.properties["final"] = (head, p)

                current.add_transition(token, new)
                nodes[head][-1].append(new)
                current = new

            index += 1

    for group in nodes[start_symbol]:
        aum.add_transition('', group[0])

    for head, body in productions.items():
        for i, production in enumerate(body):
            current = nodes[head][i][0]

            for j, token in enumerate(production):
                if token in non_terminals:
                    for group in nodes[token]:
                        current.add_transition('', group[0])

                current = nodes[head][i][j + 1]

    nfa = NFA(aum)
    return DFA.fromNFA(nfa)

def create_SLR1_Table(productions, non_terminals, terminals, start_symbol, states):
    states = sorted(states, key = lambda state: state.index)
    
    table = {sym: [(state.transitions[sym].index if sym in state.transitions else None) for state in states] for sym in terminals | {'$'} | non_terminals}
    
    for state in states:
        if state.final and state.properties['final'][0][0] == 'SS':
            table['$'][state.index] = 'Accept!'

    follow = calculate_follow(productions, terminals, non_terminals, start_symbol)
    
    for t in terminals | {'$'}:
        for state in states:
            if state.final:
                for production in state.properties['final']:
                    if production[0] != 'SS' and t in follow[production[0]]:
                        if not table[t][state.index]:
                            table[t][state.index] = production
                        else:
                            raise Exception("Bad Grammar")

    return table