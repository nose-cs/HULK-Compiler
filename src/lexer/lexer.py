from src.automaton import State
from src.regex.regex_automaton import get_regex_automaton
from src.utils import Token, UnknownToken


class Lexer:
    def __init__(self, table, eof, synchronizing_tokens=None):
        if synchronizing_tokens is None:
            synchronizing_tokens = []
        self.eof = eof
        self.automaton = self._build_automaton(table)
        self.synchronizing_automaton = self._build_automaton(synchronizing_tokens)

    @staticmethod
    def _build_automaton(table) -> State:
        start = State(None)

        for i, value in enumerate(table):
            regex, terminal = value

            si, sf = get_regex_automaton(regex)

            sf.state = (i, terminal)

            start.add_epsilon_transition(si)

        return start

    @staticmethod
    def _get_new_row_col(text, start, end, row, col):
        if end >= len(text):
            return row, col

        for j in range(start, end):
            if text[j] == '\n':
                row += 1
                col = 0
            else:
                col += 1
        return row, col + 1

    def find_next_valid_token_after_an_error(self, text, start, row, col):
        i = start
        max_pos = (i, None, None)
        current_states = self.synchronizing_automaton.epsilon_closure

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

            if len(current_states) == 0 and max_pos[1] is not None:
                row, col = self._get_new_row_col(text, start, max_pos[0], row, col)
                return max_pos[0], row, col

            max_pos = (max_pos[0] + 1, None, None)
            i += 1

        return i, row, col

    def _tokenize(self, text):
        max_pos = (0, None)

        current_states = self.automaton.epsilon_closure
        i = 0

        row, col = 1, 1

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
                yield text[max_pos[0]: max_pos[1] + 1], max_pos[2], row, col
                # update row and col
                row, col = self._get_new_row_col(text, max_pos[0], max_pos[1] + 1, row, col)
                i = max_pos[1]
                max_pos = (max_pos[1] + 1, None)
                current_states = self.automaton.epsilon_closure

            elif len(current_states) == 0 or i + 1 == len(text):
                # return an unknown token
                yield text[max_pos[0]: i], None, row, col
                # update row and col
                i, row, col = self.find_next_valid_token_after_an_error(text, i, row, col)
                max_pos = (i, None, None)
                current_states = self.automaton.epsilon_closure

            i += 1

        yield '$', self.eof, row + 1, 0

    def __call__(self, text):
        return [Token(lex, ttype, row, col) if ttype is not None else UnknownToken(lex, row, col) for
                lex, ttype, row, col in self._tokenize(text)]
