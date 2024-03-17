from src.automaton import State

def build_basic_nfa(symbol):
    initial = State(None)
    final = State(None, final = True)

    if symbol == 'ε':
        return final, final

    initial.add_transition(symbol, final)
    return initial, final

def join_nfas(nfa1 : tuple[State, State], nfa2 : tuple[State, State]):
    initial = State(None)
    final = State(None, final = True)

    initial.add_epsilon_transition(nfa1[0])
    initial.add_epsilon_transition(nfa2[0])
    
    nfa1[1].final = False
    nfa2[1].final = False

    nfa1[1].add_epsilon_transition(final)
    nfa2[1].add_epsilon_transition(final)
    
    return initial, final

def concatenate_nfas(nfa1 : tuple[State, State], nfa2 : tuple[State, State]):
    nfa1[1].add_epsilon_transition(nfa2[0])
    nfa1[1].final = False
    
    return nfa1[0], nfa2[1]

def kleene_closure(nfa : tuple[State, State]):
    initial = State(None)
    final = State(None, final = True)

    initial.add_epsilon_transition(nfa[0])
    initial.add_epsilon_transition(final)
    
    nfa[1].final = False
    
    nfa[1].add_epsilon_transition(nfa[0])
    nfa[1].add_epsilon_transition(final)
    
    return initial, final