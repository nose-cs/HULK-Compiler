from nfa import NFA

class DFAState:
    def __init__(self, final=False):
        self.final = final
        self.transitions = {}

    def add_transition(self, symbol, state):
        self.transitions[symbol] = state

class DFA:
    def __init__(self, initial_state=None):
        self.initial_state = initial_state

    def execute(self, text):
        text += '$'

        tokens = []

        max_pos = (0, None)

        current = self.initial_state
        i = 0

        while i < len(text):
            char = text[i]
            
            if char in current.transitions:
                current = current.transitions[char]
            else:
                current = None

            if current and current.final:
                max_pos = (max_pos[0], i)

            if not current and max_pos[1]:
                tokens.append(text[max_pos[0] : max_pos[1] + 1])
                i = max_pos[1]
                max_pos = (max_pos[1] + 1, None)
                current = self.initial_state

            elif not current:
                i = max_pos[0]
                max_pos = (max_pos[0] + 1, None)
                current = self.initial_state

            i += 1

        return tokens
    
    @staticmethod
    def fromNFA(nfa: NFA):
        def back_track(dic, state: DFAState, nodes):
            used = set()

            for node in nodes:
                for char in node.transitions.keys():
                    if char not in used:
                        used.add(char)

                        values = set()

                        for nnode in nodes:
                            if char in nnode.transitions:
                                values.update(nnode.transitions[char])

                                for nnnode in nnode.transitions[char]:
                                    nfa.get_epsilons(values, nnnode.epsilons)

                        if tuple(sorted(values)) not in dic:
                            dic[tuple(sorted(values))] = DFAState(any(stateNfa.final for stateNfa in values))
                            back_track(dic, dic[tuple(sorted(values))], values)

                        state.add_transition(char, dic[tuple(sorted(values))])
                                

        initial = {nfa.initial_state}
        nfa.get_epsilons(initial, nfa.initial_state.epsilons)

        state = DFAState(any(nfaState.final for nfaState in initial))

        dfa = DFA(state)

        dic = {}
        dic[tuple(sorted(initial))] = state

        back_track(dic, state, initial)

        return dfa
                