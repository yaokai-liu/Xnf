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
    with open(__dir__ / 'xnf.xnf', 'r', encoding='utf-8') as f:
        XNF_PARSER.set_rules(f.read(), start='Rules')
    XNF_PARSER.dump(cfd)
