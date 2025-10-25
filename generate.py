import os
import sys
from pathlib import Path
from xnf import *
__dir__ = Path(os.path.dirname(__file__))

ENVS = {
    "$",
    "GrammarEntry",
    "RIGHT_BRACKET",
    "SEMICOLON"
}

if __name__ == '__main__':
    if len(sys.argv) < 2:
        cfd = __dir__
    elif not os.path.isabs(sys.argv[1]):
        cfd = Path(os.getcwd()) / sys.argv[1]
    else:
        cfd = Path(sys.argv[1])
    if len(sys.argv) < 3 or sys.argv[2] != '--compact':
        compact = False
    else:
        compact = True
    with open(__dir__ / 'xLR.xnf', 'r', encoding='utf-8') as f:
        XNF_PARSER.set_rules(f.read(), start='GrammarEntry')
    XNF_PARSER.add_environment(ENVS)
    XNF_PARSER.dump(cfd / 'xLR', compact=compact)

