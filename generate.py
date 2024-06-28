import os
from pathlib import Path
from xnf import *

cfd = Path(os.path.dirname(__file__))
with open(cfd / 'regex.xnf', 'r', encoding='utf-8') as f:
    XNF_PARSER.set_rules(f.read(), start='Regexp')

if __name__ == '__main__':
    XNF_PARSER.dump(cfd)
