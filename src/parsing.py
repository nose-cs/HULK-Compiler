from abc import abstractmethod, ABC

from src.automaton import State, multiline_formatter
from src.pycompiler import Grammar, Production, Item
from src.utils import ContainerSet


class ParserError(Exception):
    def __init__(self, text, token_index):
        super().__init__(text)
        self.token_index = token_index


def compute_firsts(G: Grammar):
    first_sets = {symbol: (set() if symbol.IsNonTerminal else {symbol}) for symbol in G.nonTerminals + G.terminals}
    changed = True

    while changed:
        changed = False
        for nt in G.nonTerminals:
            for production in nt.productions:
                for symbol in production.Right:
                    before_update = len(first_sets[nt])
                    if symbol.IsTerminal and not symbol.IsEpsilon:
                        first_sets[nt].add(symbol)

                        if len(first_sets[nt]) > before_update:
                            changed = True

                        break
                    elif not symbol.IsEpsilon:
                        first_sets[nt] |= (first_sets[symbol] - {G.Epsilon})

                        if len(first_sets[nt]) > before_update:
                            changed = True

                        if G.Epsilon not in first_sets[symbol]:
                            break
                else:
                    first_sets[nt].add(G.Epsilon)
    return first_sets


def compute_follows(G: Grammar, firsts):
    follow_sets = {nt: set() for nt in G.nonTerminals}
    follow_sets[G.startSymbol].add(G.EOF)

    changed = True
    while changed:
        changed = False
        for nt in G.nonTerminals:
            for production in nt.productions:
                for i, symbol in enumerate(production.Right):
                    if symbol.IsNonTerminal:
                        before_update = len(follow_sets[symbol])

                        if i + 1 < len(production.Right):
                            next_symbol = production.Right[i + 1]
                            follow_sets[symbol] |= (firsts[next_symbol] - {G.Epsilon})

                            j = 2
                            while i + j <= len(production.Right):
                                if i + j == len(production.Right):
                                    if G.Epsilon in firsts[next_symbol]:
                                        follow_sets[symbol] |= follow_sets[nt]
                                    break
                                elif G.Epsilon in firsts[next_symbol]:
                                    next_symbol = production.Right[i + j]
                                    follow_sets[symbol] |= (firsts[next_symbol] - {G.Epsilon})
                                    j += 1
                                else:
                                    break

                        else:
                            follow_sets[symbol] |= follow_sets[nt]

                        if len(follow_sets[symbol]) > before_update:
                            changed = True
    return follow_sets


def compute_local_first(G: Grammar, firsts, preview):
    lookahead = set()

    for symbol in preview:
        if symbol.IsEpsilon:
            continue

        if symbol.IsTerminal:
            lookahead.add(symbol)
            return lookahead

        else:
            lookahead.update(firsts[symbol] - {G.Epsilon})

            if G.Epsilon not in firsts[symbol]:
                return lookahead


def build_LR0_automaton(G: Grammar):
    assert len(G.startSymbol.productions) == 1, 'Grammar must be augmented'

    start_production: Production = G.startSymbol.productions[0]
    start_item = Item(start_production, 0)
    second_item = Item(start_production, 1)

    start = State(start_item)
    second = State(second_item, True)

    start.add_transition(start_production.Right._symbols[0].Name, second)

    nodes = {start_production.Left: [[start, second]]}

    for non_terminal in G.nonTerminals:
        if non_terminal != start_production.Left:
            nodes[non_terminal] = []

            for production in non_terminal.productions:
                inicial_item = Item(production, 0)
                inicial = State(inicial_item)

                nodes[non_terminal].append([inicial])

                current = inicial

                for i, symbol in enumerate(production.Right):
                    new_item = Item(production, i + 1)
                    new = State(new_item, i + 1 == len(production.Right))

                    current.add_transition(symbol.Name, new)
                    nodes[non_terminal][-1].append(new)
                    current = new

    for group in nodes[start_production.Right[0]]:
        start.add_epsilon_transition(group[0])

    for non_terminal in G.nonTerminals:
        if non_terminal != start_production.Left:
            for i, production in enumerate(non_terminal.productions):
                current = nodes[non_terminal][i][0]

                for j, symbol in enumerate(production.Right):
                    if symbol.IsNonTerminal:
                        for group in nodes[symbol]:
                            current.add_epsilon_transition(group[0])

                    current = nodes[non_terminal][i][j + 1]

    return start


class ShiftReduceParser(ABC):
    SHIFT = 'SHIFT'
    REDUCE = 'REDUCE'
    OK = 'OK'

    def __init__(self, G, verbose=False):
        self.G = G
        self.verbose = verbose
        self.table = {}
        self._build_parsing_table()

    @abstractmethod
    def _build_parsing_table(self):
        raise NotImplementedError()

    def __call__(self, w):
        stack = [0]
        cursor = 0
        output_parse = []
        operations = []

        while cursor < len(w):
            state = stack[-1]
            lookahead = w[cursor].Name
            if self.verbose:
                print(stack, '<---||--->', w[cursor:])

            if (state, lookahead) in self.table.keys():
                action, tag = self.table[state, lookahead]

                operations.append(action)

                match action:
                    case ShiftReduceParser.OK:
                        return output_parse, operations

                    case ShiftReduceParser.SHIFT:
                        stack.append(tag)
                        cursor += 1

                    case ShiftReduceParser.REDUCE:
                        output_parse.append(tag)
                        Left, Right = tag

                        for symbol in Right:
                            if not symbol.IsEpsilon:
                                stack.pop()

                        if (stack[-1], Left.Name) in self.table and self.table[(stack[-1], Left.Name)][
                            0] == ShiftReduceParser.SHIFT:
                            stack.append(self.table[(stack[-1], Left.Name)][1])
                        else:
                            raise ParserError("Chain cannot be parsed", cursor)
            else:
                raise ParserError("Chain cannot be parsed", cursor)

        raise ParserError("Chain cannot be parsed", cursor)


class SLR1Parser(ShiftReduceParser):

    def _build_parsing_table(self):
        G = self.G.AugmentedGrammar(True)
        firsts = compute_firsts(G)
        follows = compute_follows(G, firsts)

        automaton = build_LR0_automaton(G).to_deterministic()

        index = 0
        states = {automaton: index}
        index += 1

        pending = [automaton]

        while len(pending) > 0:
            current = pending.pop()

            for symbol, list_state in current.transitions.items():
                state = list_state[0]

                if state not in states:
                    pending.append(state)
                    states[state] = index
                    index += 1

                self.table[states[current], symbol] = (ShiftReduceParser.SHIFT, states[state])

        for state in states.keys():
            if state.final:
                for node in state.state:
                    if node.state.production == G.startSymbol.productions[0] and node.state.IsReduceItem:
                        self.table[states[state], G.EOF.Name] = (ShiftReduceParser.OK, None)

        for state in states.keys():
            if state.final:
                for node in state.state:
                    if node.state.IsReduceItem:
                        if node.state.production != G.startSymbol.productions[0]:
                            for terminal in follows[node.state.production.Left]:
                                if (states[state], terminal) not in self.table:
                                    self.table[states[state], terminal.Name] = (
                                        ShiftReduceParser.REDUCE, node.state.production)
                                else:
                                    raise Exception("Bad Grammar")

    @staticmethod
    def _register(table, key, value):
        assert key not in table or table[key] == value, 'Shift-Reduce or Reduce-Reduce conflict!!!'
        table[key] = value


def expand(G: Grammar, item: Item, firsts, items: set[Item]):
    next_symbol = item.NextSymbol
    if next_symbol is None or not next_symbol.IsNonTerminal:
        return []

    lookaheads = set()

    for preview in item.Preview():
        lookaheads.update(compute_local_first(G, firsts, preview))

    for production in next_symbol.productions:
        new_item = Item(production, 0, lookaheads)

        if new_item not in items:
            items.add(new_item)
            expand(G, new_item, firsts, items)

    return items


def compress(items):
    centers = {}

    for item in items:
        center = item.Center()
        try:
            lookaheads = centers[center]
        except KeyError:
            centers[center] = lookaheads = set()
        lookaheads.update(item.lookaheads)

    return {Item(x.production, x.pos, lookahead) for x, lookahead in centers.items()}


def closure_lr1(G: Grammar, items, firsts):
    closure = ContainerSet(*items)

    new_items = ContainerSet()

    for item in items:
        new_items.set.update(expand(G, item, firsts, set()))

    closure.update(new_items)

    return compress(closure)


def goto_lr1(G: Grammar, items, symbol, firsts=None, just_kernel=False):
    assert just_kernel or firsts is not None, '`firsts` must be provided if `just_kernel=False`'
    items = frozenset(item.NextItem() for item in items if item.NextSymbol == symbol)
    return items if just_kernel else closure_lr1(G, items, firsts)


def build_LR1_automaton(G):
    assert len(G.startSymbol.productions) == 1, 'Grammar must be augmented'

    firsts = compute_firsts(G)
    firsts[G.EOF] = {G.EOF}

    start_production = G.startSymbol.productions[0]
    start_item = Item(start_production, 0, lookaheads=(G.EOF,))
    start = frozenset([start_item])

    closure = frozenset(closure_lr1(G, start, firsts))
    automaton = State(closure, any(item.IsReduceItem for item in closure))

    pending = [closure]
    visited = {closure: automaton}

    while pending:
        current = pending.pop()
        current_state = visited[current]

        for symbol in G.terminals + G.nonTerminals:
            closure = frozenset(goto_lr1(G, current, symbol, firsts))

            if len(closure) > 0:
                if closure not in visited:
                    visited[closure] = State(closure, any(item.IsReduceItem for item in closure))
                    pending.append(closure)

                current_state.add_transition(symbol.Name, visited[closure])

    automaton.set_formatter(multiline_formatter)
    return automaton


class LR1Parser(ShiftReduceParser):
    def _build_parsing_table(self):
        G = self.G.AugmentedGrammar(True)

        automaton = build_LR1_automaton(G)

        index = 0
        states = {automaton: index}
        index += 1

        pending = [automaton]

        while len(pending) > 0:
            current = pending.pop()

            for symbol, list_state in current.transitions.items():
                assert len(list_state) == 1
                state = list_state[0]

                if state not in states:
                    pending.append(state)
                    states[state] = index
                    index += 1

                self.table[states[current], symbol] = (ShiftReduceParser.SHIFT, states[state])

        for state in states.keys():
            if state.final:
                for item in state.state:
                    if item.production == G.startSymbol.productions[0] and item.IsReduceItem:
                        self.table[states[state], G.EOF.Name] = (ShiftReduceParser.OK, None)

        for state in states.keys():
            if state.final:
                for item in state.state:
                    if item.IsReduceItem:
                        if item.production != G.startSymbol.productions[0]:
                            for terminal in item.lookaheads:
                                if (states[state], terminal.Name) not in self.table:
                                    self.table[states[state], terminal.Name] = (
                                        ShiftReduceParser.REDUCE, item.production)
                                else:
                                    raise Exception(
                                        f"Grammar is not LR(1). A conflict had happened at {states[state], terminal.Name}: table[{states[state]},{terminal.Name}] = {self.table[states[state], terminal.Name]} and tried to set it to {ShiftReduceParser.REDUCE, item.production}")

    @staticmethod
    def _register(table, key, value):
        assert key not in table or table[key] == value, 'Shift-Reduce or Reduce-Reduce conflict!!!'
        table[key] = value
