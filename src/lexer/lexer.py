from src.automaton import State
from src.regex.regex_automaton import get_regex_automaton
from src.utils import Token


class Lexer:
    def __init__(self, table, eof):
        self.eof = eof
        self.automaton = self._build_automaton(table)

    @staticmethod
    def _build_automaton(table):
        start = State(None)

        for i, value in enumerate(table):
            regex, terminal = value

            si, sf = get_regex_automaton(regex)

            sf.state = (i, terminal)

            start.add_epsilon_transition(si)

        return start

    def _tokenize(self, text):
        max_pos = (0, None)

        current_states = self.automaton.epsilon_closure
        i = 0

        while i < len(text):
            char = text[i]
            new_states = set()

            for state in current_states:
                if char in state.transitions:
                    for new_state in state.transitions[char]:
                        new_states.update(new_state.epsilon_closure)

            current_states = new_states

            priority = None
            for state in current_states:
                if state.final:
                    if isinstance(state.state[0], State):
                        for nfa in state.state:
                            if nfa.final:
                                if not priority or priority > nfa.state[0]:
                                    max_pos = (max_pos[0], i, nfa.state[1])
                                    priority = nfa.state[0]
                    else:
                        if not priority or priority > state.state[0]:
                            max_pos = (max_pos[0], i, state.state[1])
                            priority = state.state[0]

            if (len(current_states) == 0 or i + 1 == len(text)) and max_pos[1] is not None:
                yield text[max_pos[0]: max_pos[1] + 1], max_pos[2]
                i = max_pos[1]
                max_pos = (max_pos[1] + 1, None)
                current_states = self.automaton.epsilon_closure

            elif len(current_states) == 0 or i + 1 == len(text):
                i = max_pos[0]
                max_pos = (max_pos[0] + 1, None)
                current_states = self.automaton.epsilon_closure

            i += 1

        yield '$', self.eof

    def __call__(self, text):
        return [Token(lex, ttype) for lex, ttype in self._tokenize(text) if ttype is not None]
