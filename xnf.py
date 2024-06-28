import re
from pathlib import Path


class Terminal(object):

    def __new__(cls, _type, _value, _lineno, _column):
        if not _value: return None
        _inst = object.__new__(cls)
        return _inst

    def __init__(self, _type, _value, _lineno, _column):
        self.type = _type
        self.value = _value if isinstance(_value, str) else _value.group(0)
        self.lineno = _lineno
        self.column = _column
        self.matched = None if isinstance(_value, str) else _value

    def __repr__(self):
        return f'Terminal({self.type}, "{self.value}", {self.lineno}, {self.column})'

    def __len__(self):
        return len(self.value)


class Lexer(object):

    def __init__(self, name: str, lineno=0, column=0, **kwargs):
        super().__init__()
        self.__TOKENS__ = dict()
        self.__ASSISTS__ = dict()
        self.__LITERALS__: list = []
        self.__PRIORITIES__ = dict()
        self.name = name
        self.lineno = lineno
        self.column = column
        if kwargs:
            self.add_patterns(**kwargs)

    @property
    def tokens(self) -> list:
        return list(self.__TOKENS__.keys())

    @property
    def assists(self) -> list:
        return list(self.__ASSISTS__.keys())

    @property
    def literal_patterns(self):
        literals = [re.escape(l) for l in self.__LITERALS__]
        return re.compile(r'|'.join(literals))

    def __check_token__(self, _token):
        return _token in self.tokens

    def __check_literal__(self, _literal):
        return _literal in self.__LITERALS__

    def __compile_token__(self, _name, _token):
        if callable(_token):
            return _token

        def __match(_input):
            pattern = re.compile(_token)
            result = pattern.match(_input)
            return Terminal(_name, result, self.lineno, self.column)

        return __match

    def __compile_assist__(self, _name, _assist):
        if callable(_assist):
            return _assist

        def __assist(_input):
            pattern = re.compile(_assist)
            result = pattern.match(_input)
            return result.group(0) if result else ''

        return __assist

    def add_literals(self, literals):
        self.__LITERALS__ += literals

    def add_patterns(self, priority=0, **kwargs):
        pri_keys = self.__PRIORITIES__.get(priority)
        pri_keys = pri_keys or []
        for key, value in kwargs.items():
            if key == '_error':
                raise SyntaxError("key '_error' is not allowed set as a pattern!")
            if key.startswith('_'):
                self.__ASSISTS__.update({key: self.__compile_assist__(key, value)})
            elif key == 'literals':
                self.add_literals(value)
            else:
                self.__TOKENS__.update({key: self.__compile_token__(key, value)})
                pri_keys.append(key)
        self.__PRIORITIES__.update({priority: pri_keys})

    def __call__(self, priority=0):
        def __decorator(__func):
            name = __func.__name__
            if name == '_error':
                self.__ASSISTS__[name] = __func
                return __func
            target = self.__ASSISTS__ if name.startswith('_') else self.__TOKENS__
            _compiler = Lexer.__compile_assist__ if name.startswith('_') else Lexer.__compile_token__

            def __wrapper(_input):
                __match = _compiler(self, name, __func.__doc__)
                return __func(__match(_input))

            target[name] = __wrapper
            if not name.startswith('_'):
                p = priority or 1
                if not self.__PRIORITIES__.get(p):
                    self.__PRIORITIES__[p] = [name]
                else:
                    self.__PRIORITIES__[p].append(name)
            return __func

        return __decorator

    def __pass_space(self, _input, lineno, column):
        ignore = self.__ASSISTS__.get('_ignore') or (lambda x: '')
        newline = self.__ASSISTS__.get('_newline') or (lambda x: '')
        _i, _n = len(ignore(_input)), len(newline(_input))
        while _i or _n:
            if _i:
                _input = _input[_i:]
                column += _i
            if _n:
                _input = _input[_n:]
                lineno, column = lineno + 1, 0
            _i, _n = len(ignore(_input)), len(newline(_input))

        return _input, lineno, column

    def __error__(self, _input, lineno, column):
        if self.__ASSISTS__.get('_error'):
            self.__ASSISTS__['_error'](_input, lineno, column)
        else:
            raise SyntaxError(f"""<{self.name}> Unrecognized symbol "{_input[0]}" at line {lineno} col {column}.""")

    def __match(self, _input, **kwargs):
        self.lineno = kwargs.get('lineno') or 0
        self.column = kwargs.get('colpos') or 0
        if kwargs.get('mode') == 'longest':
            result, _type = None, None
            for p in sorted(self.__PRIORITIES__.keys(), reverse=True):
                for key in self.__PRIORITIES__[p]:
                    _res = self.__TOKENS__[key](_input)
                    if _res.span()[1] > result.span()[0]:
                        result, _type = _res, key
            if result:
                return result
            elif self.literal_patterns.match(_input):
                res = self.literal_patterns.match(_input)
                return Terminal(f'"{res.group(0)}"', res, self.lineno, self.column)
            else:
                return None
        # elif kwargs.get('mode') == 'fastest':
        else:
            for p in sorted(self.__PRIORITIES__.keys(), reverse=True):
                for key in self.__PRIORITIES__[p]:
                    result = self.__TOKENS__[key](_input)
                    if result:
                        return result
            if self.literal_patterns.match(_input):
                res = self.literal_patterns.match(_input)
                return Terminal(f'"{res.group(0)}"', res, self.lineno, self.column)
            return None

    def lex(self, _input, token=None, **kwargs):
        if not token:
            return self.__match(_input)
        self.lineno = kwargs.get('lineno') or 0
        self.column = kwargs.get('colpos') or 0
        if token == '_LITERAL_':
            if self.literal_patterns.match(_input):
                res = self.literal_patterns.match(_input)
                return Terminal(f'"{res.group(0)}"', res, self.lineno, self.column)
            else:
                return None
        return self.__TOKENS__[token](_input)

    def tokenize(self, _input, **kwargs):
        lineno = kwargs.get('lineno') or 0
        column = kwargs.get('column') or 0
        _input, lineno, column = self.__pass_space(_input, lineno, column)
        while _input:
            kwargs.update({'lineno': lineno, 'column': column})
            token = self.__match(_input, **kwargs)
            if not token:
                self.__error__(_input, lineno, column)
                return None
            yield token
            lineno = lineno
            column = column + len(token.value)
            _input = _input[len(token.value):]
            _input, lineno, column = self.__pass_space(_input, lineno, column)


# xParse Normal Format: expressions to describe the grammar of xParse.
XNF_LEXER = Lexer('__XNF_LEXER__', **{
    'IDENTIFIER': r"([a-zA-Z][a-zA-Z0-9_]*)([a-zA-Z][a-zA-Z0-9_]+)?\b",
    'ASSIGNER': r'\=',
    'SPLITER': r'\|',
    'EOL': r'\;',
    '_ignore': r'[ \t]+',
    '_newline': r'\n+',
    # 'LITERAL': r'\".+?\"', // no literal for xParse token
})


class Rule(object):

    def __init__(self, name: str, target: str, items: list[str], action: callable = None):
        self.name = name
        self.target = target
        self.items: tuple = tuple(items)
        self.ACTION = action

    def __getitem__(self, item):
        return self.items[item]

    def __len__(self):
        return len(self.items)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and hash(self) == hash(other)

    def __hash__(self):
        return hash((self.target, self.name, self.items))

    def __repr__(self):
        return f"\"{self.name}\""

    def __str__(self):
        return f"{self.name}\": \"{self.target} -> {' '.join(self.items)}"

    def __call__(self, products):
        if self.ACTION is None:
            return products
        return self.ACTION(products)


class LrItem(object):
    def __init__(self, rule: Rule, lookahead: str, pos: int):
        self.rule = rule
        self.lookahead = lookahead
        self.pos = pos

    def __eq__(self, other):
        return self.__class__ == other.__class__ and hash(self) == hash(other)

    def __hash__(self):
        return hash((self.rule, self.lookahead, self.pos))

    @property
    def is_end(self):
        return self.pos >= len(self.rule)

    @property
    def current(self):
        return self.rule[self.pos] if self.pos < len(self.rule) else None

    @property
    def ahead(self):
        return self.rule[self.pos + 1] if self.pos + 1 < len(self.rule) else None

    @property
    def remain(self):
        return self.rule[self.pos:] if self.pos < len(self.rule) else []

    def __repr__(self):
        # return f"({self.rule.name}, {self.pos}, {self.lookahead})"
        return f"{self}"

    def next(self):
        if self.pos + 1 > len(self.rule): return None
        return LrItem(self.rule, self.lookahead, self.pos + 1)

    def __str__(self):
        return '"' + self.rule.target + ' -> ' \
            + ' '.join(self.rule.items[:self.pos]) + ' * ' \
            + ' '.join(self.rule.items[self.pos:]) + f' [{self.lookahead}, {self.rule.name}]' \
            + '"'

    def __and__(self, other):
        return self.rule == other.rule and self.pos == other.pos


def in_core(items1: set[LrItem], items2: set[LrItem]) -> bool:
    for item1 in items1:
        if not any({item1 & item2 for item2 in items2}):
            return False
    return True


def __build_rules__(xnf_tokens):
    status, target, items, rules = 0, '', [], []
    count = 0

    def accept_token(_token: Terminal):
        nonlocal status, target, items, rules, count
        if status == 0 and _token.type == 'IDENTIFIER':
            target = _token.value
            status = 1
            return True
        elif status == 1 and _token.type == 'ASSIGNER':
            status = 2
            return True
        elif status == 2 and _token.type == 'IDENTIFIER':
            items.append(_token.value)
            return True
        elif status == 2 and _token.type == 'SPLITER':
            rule = Rule(f'{target}_{count}', target, items)
            rules.append(rule)
            items = []
            count += 1
            return True
        elif status == 2 and _token.type == 'EOL':
            rule = Rule(f'{target}_{count}', target, items)
            rules.append(rule)
            items = []
            status = 0
            count = 0
            return True
        else:
            return False

    for _ in xnf_tokens:
        assert accept_token(_), f"Terminal {_} has no been accepted!"
    assert status == 0, "EOF occurs!"
    return rules


class Parser(object):

    def __init__(self, name: str, **kwargs):
        super().__init__()
        self.__RULES__ = set()
        self.__TOKENS__ = set()
        self.__TARGETS__ = dict()
        self.__FIRST_SET__ = dict()
        self.__FOLLOW_SET__ = dict()
        self.__START__ = None
        self.__LEXER__ = kwargs.get('lexer') or None
        self.lineno = kwargs.get("lineno") or 0
        self.column = kwargs.get("column") or 0
        self._error = None
        self.name = name

    @property
    def tokens(self):
        return self.__TOKENS__

    @property
    def rules(self):
        return self.__RULES__

    @property
    def targets(self):
        return set(self.__TARGETS__.keys())

    def set_rules(self, _input, start: str):
        tokens = self.__LEXER__.tokenize(_input)
        rules = __build_rules__(tokens)
        for rule in rules:
            if rule.target not in self.__TARGETS__:
                self.__TARGETS__[rule.target] = set()
            self.__RULES__.add(rule)
            self.__TARGETS__[rule.target].add(rule)
            self.__TOKENS__.update(set(rule.items))
        self.__extend_grammar__(start)
        self.__update_first_set__()
        self.__update_follow_set__()

    def __first_set_of__(self, _items):
        set1 = {"#"}
        for item in _items:
            set1.update(self.__FIRST_SET__[item])
            if "#" not in self.__FIRST_SET__[item]:
                set1.remove("#")
                break
        return set1

    def first_set_of(self, _items: list[str]):
        s = set()
        for item in _items:
            s |= self.__FIRST_SET__[item] - {"#"}
            if "#" not in self.__FIRST_SET__[item]: return s
        return s | {"#"}

    def follow_set_of(self, _item: str):
        return self.__FOLLOW_SET__[_item]

    def __extend_grammar__(self, start: str):
        rule = Rule("__EXTEND_RULE__", '~', [start])
        self.__RULES__.add(rule)
        self.__TOKENS__.add(start)
        self.__TARGETS__['~'] = {rule}
        self.__START__ = start

    def __update_first_set__(self):
        self.__FIRST_SET__.clear()
        for _ in self.__TOKENS__:
            self.__FIRST_SET__[_] = set() if _ in self.__TARGETS__ else {_}
        self.__FIRST_SET__['~'] = self.__FIRST_SET__[self.__START__]
        for _ in range(50):  # rough but working
            self.__update_first_set_core__()

    def __update_first_set_core__(self):
        for rule in self.__RULES__:
            if len(rule.items) == 0:
                self.__FIRST_SET__[rule.target].add("#")
                continue
            for item in rule.items:
                set1 = self.__FIRST_SET__[item]
                self.__FIRST_SET__[rule.target].update(set1 - {"#"})
                if "#" not in set1: break
            else:
                self.__FIRST_SET__[rule.target].add("#")

    def __update_follow_set__(self):
        self.__FOLLOW_SET__.clear()
        for _ in self.__TOKENS__:
            self.__FOLLOW_SET__[_] = {"#"}
        self.__FOLLOW_SET__[self.__START__].add('$')
        self.__FOLLOW_SET__['~'] = self.__FOLLOW_SET__[self.__START__]
        for _ in range(50):  # rough but working
            self.__update_follow_set_core__()
        for _ in self.__TOKENS__:
            self.__FOLLOW_SET__[_].remove("#")

    def __update_follow_set_core__(self):
        for rule in self.__RULES__:
            if len(rule) == 0:
                continue
            for i, item in enumerate(rule[:-1]):
                set1 = self.__first_set_of__(rule[i + 1:])
                self.__FOLLOW_SET__[item].update(set1)
                if "#" in set1:
                    set2 = self.__FIRST_SET__[rule.target]
                    self.__FOLLOW_SET__[item].update(set2)
            set2 = self.__FOLLOW_SET__[rule.target]
            self.__FOLLOW_SET__[rule[-1]].update(set2)

    def __item_closure__(self, items: set[LrItem]):
        _closure = items.copy()
        while True:
            extend = set()
            for lr_item in _closure:
                if lr_item.current is None: continue
                if lr_item.current in self.__TARGETS__:
                    extend.update(self.__item_closure_of__(lr_item))
            if len(extend - _closure) == 0: break
            _closure.update(extend)
        _a = {_.current for _ in _closure}
        _c_by_t = {t: {_ for _ in _closure if _.current == t} for t in _a}
        return _closure, _c_by_t

    def __item_closure_of__(self, lr_item: LrItem):
        extend = set()
        rules = [_ for _ in self.__TARGETS__[lr_item.current]]
        for _rule in rules:
            _set = self.first_set_of(lr_item.remain[1:])
            extend.update({LrItem(_rule, a, 0) for a in _set - {'#'}})
            if "#" in _set:
                extend.add(LrItem(_rule, lr_item.lookahead, 0))
        return extend

    def build(self):
        i, state = 0, tuple()
        states, table = [state], {state: dict()}
        target = {LrItem(_, "$", 0) for _ in XNF_PARSER.__TARGETS__['~']}
        cache = {state: self.__item_closure__(target)}
        while i < len(states):
            state = states[i]
            _closure, _c_by_t = cache[state]
            reduces = _c_by_t.pop(None) if None in _c_by_t else set()
            for _ in reduces:
                assert _.lookahead not in table[state], \
                    f""" Conflicting reduce rules: {reduces}, state: {state} """
                table[state][_.lookahead] = _.rule.name
            for t in _c_by_t:
                target = {_.next() for _ in _c_by_t[t]}
                for s in cache:
                    if len(target - cache[s][0]) == 0:
                        table[state][t] = s
                        break
                else:
                    _n_state = state + (t,)
                    states.append(_n_state)
                    table[_n_state] = dict()
                    cache[_n_state] = self.__item_closure__(target)
                    table[state][t] = _n_state
            i += 1
        return table, cache

    def build_compact(self):
        table, lr_items = self.build()

        return table, lr_items

    def dump(self, dest_dir: str, compact: bool = False):
        dest_dir = Path(dest_dir)
        table, lr_items = self.build_compact() if compact else self.build()
        rules = sorted(self.rules, key=lambda r: r.name)
        with open(dest_dir / 'tokens.json', 'w', encoding='utf-8') as f:
            f.write(str({
                'terminal': list(self.tokens - self.targets),
                'non-terminal': list(self.targets),
            }).replace("'", '"'))
        with open(dest_dir / 'rules.json', 'w', encoding='utf-8') as f:
            f.write(str({str(rule) for rule in rules}).replace("'", '"'))
        with open(dest_dir / 'first_set.json', 'w') as f:
            lines = [f"'{t}': {list(s)}".replace("'", '"')
                     for t, s in self.__FIRST_SET__.items()]
            f.write('{' + ','.join(lines) + '}')
        with open(dest_dir / 'follow_set.json', 'w') as f:
            lines = [f"'{t}': {list(s)}".replace("'", '"')
                     for t, s in self.__FOLLOW_SET__.items()]
            f.write('{' + ','.join(lines) + '}')
        with open(dest_dir / 'machine.json', 'w') as f:
            f.write(str({
                f"({', '.join(i)})": {
                    t: (n if isinstance(n, str) else f"({', '.join(n)})") for t, n in s.items()
                } for i, s in table.items()
            }).replace("'", '"'))
        with open(dest_dir / 'lr_items.json', 'w') as f:
            f.write(str({
                f"({', '.join(s)})": list(r[0]) for s, r in lr_items.items()
            }).replace("'", '"'))


XNF_PARSER = Parser('XNF', lexer=XNF_LEXER)

__all__ = ['LrItem', 'Rule', 'XNF_PARSER']
