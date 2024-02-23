from nfa import NFA, NFAState

class BuildNFA:
    global_index = 0

    def build_basic_nfa(self, symbol):
        initial = NFAState(self.global_index)
        final = NFAState(self.global_index + 1, True)
        self.global_index += 2

        if symbol == '':
            return NFA(final, final)

        initial.add_transition(symbol, final)
        return NFA(initial, final)

    def join_nfas(self, nfa1, nfa2):
        initial = NFAState(self.global_index)
        final = NFAState(self.global_index + 1, True)
        self.global_index += 2

        initial.add_transition('', nfa1.initial_state)
        initial.add_transition('', nfa2.initial_state)
        
        nfa1.final_state.final = False
        nfa2.final_state.final = False
        
        nfa1.final_state.add_transition('', final)
        nfa2.final_state.add_transition('', final)
        
        return NFA(initial, final)

    def concatenate_nfas(self, nfa1, nfa2):
        nfa1.final_state.add_transition('', nfa2.initial_state)
        nfa1.final_state.final = False
        
        return NFA(nfa1.initial_state, nfa2.final_state)

    def kleene_closure(self, nfa):
        initial = NFAState(self.global_index)
        final = NFAState(self.global_index + 1, True)

        self.global_index += 2
        
        initial.add_transition('', nfa.initial_state)
        initial.add_transition('', final)
        
        nfa.final_state.final = False
        
        nfa.final_state.add_transition('', nfa.initial_state)
        nfa.final_state.add_transition('', final)
        
        return NFA(initial, final)
