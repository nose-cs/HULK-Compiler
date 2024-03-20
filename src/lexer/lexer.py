from src.utils import Token
from src.automaton import State
from src.pycompiler import Terminal
from src.regex.regex_automaton import get_regex_automaton

def get_lexer(regexs: list[tuple[str, Terminal]]):
    inicial = State(None)

    for i, value in enumerate(regexs):
        regex, terminal = value
        
        si, sf = get_regex_automaton(regex)
        
        sf.state = (i, terminal)

        inicial.add_epsilon_transition(si)
    
    return inicial

def get_tokens(inicial : State, text : str):
        tokens = []

        max_pos = (0, None)

        current_states = inicial.epsilon_closure
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
                tokens.append(Token(text[max_pos[0] : max_pos[1] + 1], max_pos[2]))
                i = max_pos[1]
                max_pos = (max_pos[1] + 1, None)
                current_states = inicial.epsilon_closure

            elif (len(current_states) == 0 or i + 1 == len(text)):
                i = max_pos[0]
                max_pos = (max_pos[0] + 1, None)
                current_states = inicial.epsilon_closure

            i += 1

        return tokens