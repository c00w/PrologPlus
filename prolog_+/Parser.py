from Types import Statement, Predicate, Variable, Atom, Conjunction, Disjunction, isvariable, Equation, Negation

def _parse(lines):
    CE = set()
    for source in lines.split("\n"):
        CE.add(_parse_statement(source))
    return CE

def _parse_statement(source):

    source = source.replace("\t", "")
    source = source.replace(" ", "")

    if ':' == source[0]:
        return Equation(source[1:])

    if '=|' in source:
        lhs, rhs = source.split('=|', 1)
        lhs = _parse_term(lhs)
        rhs = float(rhs)
        lhs.set_prob(rhs)
        return Statement(lhs, None)

    if ':' not in source or '.' not in source:
        raise SyntaxError(": or . not in line:%s" % source)
    lhs, rhs = source.split(":", 1)
    if rhs != '.':
        rhs = _parse_term(rhs[:-1])
    else:
        rhs = None
    lhs = _parse_term(lhs)
    if rhs == None:
        lhs.set_prob(1.0)
    return Statement(lhs, rhs)

def count(source):
    count = 0
    for item in source:
        if item == '(':
            count += 1
        if item == ')':
            count -= 1
    return count

def _parse_term(source):
    if ',' in source and count(source[:source.index(',')]) == 0 and count(source[source.index(',')+1:]) == 0:
        return _parse_conj(source)
    elif '|' in source and count(source[:source.index('|')]) == 0 and count(source[source.index('|')+1:]) == 0:
        return _parse_disj(source)
    else:
        return _parse_pred(source)

def _parse_conj(source):
    if source[0] == '[':
        left = source[1:source.index(']')]
        right = source[source.index(']')+1:]
    else:
        left, right = source.split(',', 1)

    left = _parse_term(left)
    right = _parse_term(right)
    return Conjunction(left, right)

def _parse_disj(source):
    if source[0] == '[':
        left = source[1:source.index(']')]
        right = source[source.index(']')+1:]
    else:
        left, right = source.split('|', 1)

    left = _parse_term(left)
    right = _parse_term(right)
    return Disjunction(left, right)

def _parse_item(source):
    if '(' in source:
        return _parse_pred(source)
    if isvariable(source):
        return Variable(source)
    else:
        return Atom(source)

def _parse_pred(source):
    if '!' == source[0]:
        return _parse_negation(source)

    if '(' not in source or ')' not in source:
        raise SyntaxError('( or ) not in predicate: %s' % source)

    if source[-1] != ')':
        raise SyntaxError('Did not end with ")": %s' % source)

    name = source[:source.index('(')]
    items = source[source.index('(')+1:-1]
    items = items.split(',')
    items = map(_parse_item, items)
    return Predicate(name, items)


def _parse_negation(source):
    return Negation(_parse_pred(source[1:]))

# PY.TEST tests

def test_load():
    assert True

def test_Parser():
    source = "A(a):."
    assert _parse(source)

def test_Conj_disj():
    source = "A(a)|A(b):A(b),A(c)."
    assert _parse(source)

def test_Nested():
    source = "A(B(c),D(c)):."
    assert _parse(source)

def test_Statement():
    test = ['A(b):.','A(X):B(X),C(X).', 'A(X),B(X):C(X),D(d).']
    for state in test:
        assert _parse(state)
def test_EQN():
    test = [': x= x**2-36', ':y+x']
    for state in test:
        assert _parse(state)

def test_negation_type():
    a = _parse_pred('!B(a)')
    assert isinstance(a, Negation)
