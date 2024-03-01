import sys
sys.path.insert(1, '..')

from parser.parser import ParserSLR1
from parser.utils import EPSILON
from build_nfa import BuildNFA
from automaton.dfa import DFA

class Regex:
    def __init__(self, regex) -> None:
        terminals = {'á', 'é', 'í', 'ó', 'ú',
                    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 
                    'm', 'n', 'ñ', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w',
                    'x', 'y', 'z',
                    'Á', 'É', 'Í', 'Ó', 'Ú',
                    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 
                    'M', 'N', 'Ñ', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W',
                    'X', 'Y', 'Z',
                    '.', ',', ';', ':', '´', '`', '[', ']', '(', ')', '{', '}', '!', '?', '¿', '¡',
                    '¨', '+', '-', '\\', '*', '|', '^', '¬', '&', '%', '$', '#', '·', '@', '"',
                    'º', 'ª', '/', '_', "'", '<', '>'}

        non_terminals = {'EE', 'TT', 'FF', 'AA'}

        productions = {
            'EE': [['EE', '|', 'TT'], ['TT']],
            'TT': [['TT', 'FF'], ['FF']],
            'FF': [['FF', '*'], ['AA']],
            'AA': [['á'], ['é'], ['í'], ['ó'], ['ú'],
                ['a'], ['b'], ['c'], ['d'], ['e'], ['f'], ['g'], ['h'], ['i'], ['j'], ['k'], ['l'], 
                ['m'], ['n'], ['ñ'], ['o'], ['p'], ['q'], ['r'], ['s'], ['t'], ['u'], ['v'], ['w'],
                ['x'], ['y'], ['z'],
                ['Á'], ['É'], ['Í'], ['Ó'], ['Ú'],
                ['A'], ['B'], ['C'], ['D'], ['E'], ['F'], ['G'], ['H'], ['I'], ['J'], ['K'], ['L'], 
                ['M'], ['N'], ['Ñ'], ['O'], ['P'], ['Q'], ['R'], ['S'], ['T'], ['U'], ['V'], ['W'],
                ['X'], ['Y'], ['Z'],
                ['.'], [','], [';'], [':'], ['´'], ['`'], ['{'], ['}'], ['!'], ['?'], ['¿'], ['¡'],
                ['¨'], ['+'], ['-'], ['^'], ['¬'], ['&'], ['%'], ['#'], ['·'], ['@'], ['"'],
                ['º'], ['ª'], ['/'], ['_'], ["'"], ['<'], ['>'],
                ['\\', '*'], ['\\', '|'], ['\\', '$'], ['\\', '['], ['\\', ']'], ['\\', '('], ['\\', ')'],
                ['(', 'EE', ')'], ['[', 'a', '.', '.', 'z', ']'], ['[', 'A', '.', '.', 'Z', ']']]
        }

        start_symbol = 'EE'

        def getProductionEvaluate(production):
            build = BuildNFA()
            
            match production:
                case ('EE', 0):
                    return lambda node: build.join_nfas(node.childs[2].evaluate(), node.childs[0].evaluate())
                case ('EE', 1): 
                    return lambda node: node.childs[0].evaluate()
                case ('TT', 0): 
                    return lambda node: build.concatenate_nfas(node.childs[1].evaluate(), node.childs[0].evaluate())
                case ('TT', 1): 
                    return lambda node: node.childs[0].evaluate()
                case ('FF', 0): 
                    return lambda node: build.kleene_closure(node.childs[1].evaluate())
                case ('FF', 1): 
                    return lambda node: node.childs[0].evaluate()
                case ('AA', 101):
                    return lambda node: node.childs[1].evaluate()

            if production[1] == 102:
                values = ['c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 
                    'm', 'n', 'ñ', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w',
                    'x', 'y', 'z']
                
                result = build.join_nfas(build.build_basic_nfa('a'), build.build_basic_nfa('b'))

                for value in values:
                    result = build.join_nfas(result, build.build_basic_nfa(value))

                return lambda node: result
            
            if production[1] == 103:
                values = ['C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 
                    'M', 'N', 'Ñ', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W',
                    'X', 'Y', 'Z']
                
                result = build.join_nfas(build.build_basic_nfa('A'), build.build_basic_nfa('B'))

                for value in values:
                    result = build.join_nfas(result, build.build_basic_nfa(value))

                return lambda node: result

            return lambda node: build.build_basic_nfa(node.childs[0].text)

        parser = ParserSLR1(productions, non_terminals, terminals, start_symbol, getProductionEvaluate)

        root = parser.parse([regex[i] for i in range(len(regex))])

        nfa = root.evaluate()
        dfa, states = DFA.fromNFA(nfa)

        self.nfa = nfa
        self.dfa = dfa

    def execute(self, string: str):
        return self.dfa.execute(string)