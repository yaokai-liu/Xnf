import os
import sys
from pathlib import Path
from xnf import *

__dir__ = Path(os.path.dirname(__file__))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        cfd = __dir__
    elif not os.path.isabs(sys.argv[1]):
        cfd = Path(os.getcwd()) / sys.argv[1]
    else:
        cfd = sys.argv[0]
    if len(sys.argv) < 3 or sys.argv[2] != '--compact':
        compact = False
    else:
        compact = True
    with open(__dir__ / 'xCONF.xnf', 'r', encoding='utf-8') as f:
        XNF_PARSER.set_rules(f.read(), start='Object')
    XNF_PARSER.dump(cfd / 'xCONF', compact=compact)
    XNF_PARSER.clear()
    path_rule = "Path = Path DOT KEY | Path LEFT_SQUARE_BRACKET NUMBER RIGHT_SQUARE_BRACKET | DOT KEY | KEY;"
    XNF_PARSER.set_rules(path_rule, start='Path')
    XNF_PARSER.dump(cfd / 'Path', compact=compact)
