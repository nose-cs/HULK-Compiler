class NFAState:
    def __init__(self, index, final=False):
        self.final = final
        self.transitions = {}
        self.epsilons = set()
        self.index = index

    def add_transition(self, symbol, state):
        if symbol == '':
            self.epsilons.add(state)

        elif symbol in self.transitions:
            self.transitions[symbol].add(state)
        else:
            self.transitions[symbol] = {state}

    def __lt__(self, other):
        self.index < other.index

class NFA:
    def __init__(self, initial_state=None, final_state=None):
        self.initial_state = initial_state
        self.final_state = final_state

    def add_transition(self, origin, symbol, destiny):
        origin.add_transition(symbol, destiny)

    def get_epsilons(self, states: set, epsilons: list):
        states.update(epsilons)

        for e in epsilons:
            self.get_epsilons(states, e.epsilons)

    def execute(self, text):
        text += '$'

        tokens = []

        max_pos = (0, None)

        initial = {self.initial_state}
        self.get_epsilons(initial, self.initial_state.epsilons)

        current_states = initial
        i = 0

        while i < len(text):
            char = text[i]
            new_states = set()

            for state in current_states:
                if char in state.transitions:
                    new_states.update(state.transitions[char])
                    for new_estado in state.transitions[char]:
                        self.get_epsilons(new_states, new_estado.epsilons)

            current_states = new_states

            if any(state.final for state in current_states):
                max_pos = (max_pos[0], i)

            if len(current_states) == 0 and max_pos[1]:
                tokens.append(text[max_pos[0] : max_pos[1] + 1])
                i = max_pos[1]
                max_pos = (max_pos[1] + 1, None)
                current_states = initial

            elif len(current_states) == 0:
                i = max_pos[0]
                max_pos = (max_pos[0] + 1, None)
                current_states = initial

            i += 1

        return tokens