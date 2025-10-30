import os
from pathlib import Path
from argparse import ArgumentParser, BooleanOptionalAction, ArgumentError, ArgumentTypeError
from xnf import *

if __name__ == '__main__':
    parser = ArgumentParser(description="parse XNF grammar file and generate automatons in json")
    parser.add_argument('grammar', type=Path, help='the grammar file')
    parser.add_argument('entry', type=str, help='the grammar entry')
    parser.add_argument('-e', '--environments', type=str, help='environments the grammar will be applied')
    parser.add_argument('-o', '--output-directory', type=Path, help='the output directory')
    parser.add_argument('-c', '--compact', type=bool, action=BooleanOptionalAction, help='generate the LR(0) version')
    args = parser.parse_args()
    args.grammar = Path(os.getcwd()) / args.grammar
    args.output_directory = Path(os.getcwd()) / args.output_directory if args.output_directory else Path(os.getcwd())
    with open(args.grammar, 'r', encoding='utf-8') as f:
        XNF_PARSER.set_rules(f.read(), start=args.entry)
    if args.environments:
        args.environments = set(args.environments.split(','))
        XNF_PARSER.add_environment(args.environments)
    XNF_PARSER.dump(args.output_directory, compact=args.compact)
