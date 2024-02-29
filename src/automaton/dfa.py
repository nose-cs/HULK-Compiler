from nfa import NFA

class DFAState:
    def __init__(self, index, final=False):
        self.final = final
        self.transitions = {}
        self.properties = {}
        self.index = index

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
        def back_track(dic, state: DFAState, nodes, states, gi):
            used = set()

            for node in nodes:
                for char in node.transitions.keys():
                    if char not in used:
                        used.add(char)

                        if char == 'T' and state.index == 0:
                            pass

                        values = set()

                        for nnode in nodes:
                            if char in nnode.transitions:
                                values.update(nnode.transitions[char])

                                for nnnode in nnode.transitions[char]:
                                    nfa.get_epsilons(values, nnnode.epsilons)

                        tsv = tuple(sorted(values, key = lambda nfaState: nfaState.index))

                        if tsv not in dic:
                            new_state = DFAState(gi.get_global_index(), any(stateNfa.final for stateNfa in values))
                            
                            all_property_keys = set(key for nnode in values for key in nnode.properties)
                            new_state.properties = {key: [nnode.properties[key] for nnode in values if key in nnode.properties] for key in all_property_keys}

                            states.append(new_state)
                            dic[tsv] = new_state
                            state.add_transition(char, new_state)
                            back_track(dic, new_state, values, states, gi)
                        else:
                            state.add_transition(char, dic[tsv])

        class global_index:
            global_index = 0

            def get_global_index(self):
                self.global_index += 1
                return self.global_index - 1

        initial = {nfa.initial_state}
        nfa.get_epsilons(initial, nfa.initial_state.epsilons)

        gi = global_index()

        state = DFAState(gi.get_global_index(), any(nfaState.final for nfaState in initial))

        all_property_keys = set(key for node in initial for key in node.properties)
        state.properties = {key: [node.properties[key] for node in initial if key in node.properties] for key in all_property_keys}

        states = [state]

        dfa = DFA(state)

        dic = {}
        dic[tuple(sorted(initial, key = lambda nfaState: nfaState.index))] = state

        back_track(dic, state, initial, states, gi)

        return dfa, states
                