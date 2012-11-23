from copy import deepcopy, copy
from Types import Negation

def search(CE, term):
    prob = search_solutions(CE, term)
    if prob is None:
        return 'Unknown'
    probability = 0.0
    for p, mapping in prob:
        probability = probability + p - p * probability
    return probability

def search_expr(CE, var):
    usefull = [eqn for eqn in CE if eqn.determines(var) != None]
    usefull.sort(key=lambda x:len(x.determines(var)))
    for eqn in usefull:
        new_ce = deepcopy(CE)
        new_ce.remove(eqn)
        result = eqn.solve(var, new_ce)
        if result:
            return result
    return None

def find_unify(Pred, Statement):
    return Statement.find_unify()

def determination_list(CE, Pred):
    poss = []
    for Statement in CE:
        det = Statement.determines(Pred)
        if det is not None:
            for mapping in det:
                poss.append((Statement, mapping))
    return poss

def search_solutions(CE, term):

    if isinstance(term, Negation):
        mappings = search_solutions(CE, term.child)
        if mappings is None:
            return None
        return [(1.0 - prob if prob is not None else None, mapping) for prob, mapping in mappings]

    poss = determination_list(CE, term)
    poss.sort(key=lambda x: int(x[1] != {}))

    results = []
    for state, mapping in poss:
        nCE = deepcopy(CE)
        if state in nCE:
            nCE.remove(state)
        new_state = state.unify(mapping, nCE)
        #print nCE, CE, state
        if new_state.solutions(nCE):
            new_state.update_prob()
            results.append((new_state.prob(term), mapping))
    if results:
        return results
    return None

def test_recurse():
    import Parser
    source = "A(a):A(a)."
    CE = Parser._parse(source)
    assert search(CE, Parser._parse_pred('A(a)')) == 'Unknown'

def test_search():
    import Parser
    source = "A(a):."
    CE = Parser._parse(source)
    assert search(CE, Parser._parse_pred('A(a)')) == 1.0

    source = "A(X):."
    CE = Parser._parse(source)
    assert search(CE, Parser._parse_pred('A(a)')) == 1.0

def test_search_compl():
    import Parser
    source = "A(X):B(b).\nB(b):."
    Pred = Parser._parse_pred('A(a)')
    b = Parser._parse_pred('B(b)')
    CE = Parser._parse(source)

    assert search(CE, b) == 1.0
    assert search(CE, Pred) == 1.0

    count_det = 0
    for state in CE:
        if state.determines(Pred) is not None:
            count_det += 1
            mapping = state.determines(Pred)
            new_state = state.unify(mapping[0], CE)
    assert count_det == 1
    print new_state.solutions(CE)
    assert new_state.solutions(CE) == True

def test_search_compl_neg():
    import Parser
    source = "A(X):!B(b).\n!B(b):."
    Pred = Parser._parse_pred('A(a)')
    varPred = Parser._parse_pred('A(X)')
    notb = Parser._parse_pred('!B(b)')
    b = Parser._parse_pred('B(b)')
    CE = Parser._parse(source)

    assert search(CE, notb) == 1.0
    assert search(CE, b) == 0.0
    count_det = 0
    for state in CE:
        if state.determines(Pred) is not None:
            count_det += 1
            mapping = state.determines(Pred)
            new_state = state.unify(mapping[0], CE)
    assert count_det == 1
    assert new_state.solutions(CE) == True
    print search(CE, Pred)
    assert search(CE, varPred) == 1.0
    assert search(CE, Pred) == 1.0

def test_search_unknown_not_solutions():
    import Parser
    source = "A(X):B(X).\n A(c):."
    Pred = Parser._parse_pred('A(a)')
    CE = Parser._parse(source)
    assert search(CE, Pred) == 'Unknown'

    source = "A(a):B(X).\n A(c):."
    Pred = Parser._parse_pred('A(a)')
    CE = Parser._parse(source)
    assert search(CE, Pred) == 'Unknown'

def test_search_and_unify():
    import Parser
    source = "A(a):B(X),C(X).\nB(c):.\nC(d):."
    Pred = Parser._parse_pred('A(a)')
    CE = Parser._parse(source)
    assert search(CE, Pred) is not True
    assert search(CE, Pred) is not False
    assert search(CE, Pred) == 'Unknown'

    source = "A(a):B(X),C(X).\nB(c):.\nC(c):."
    Pred = Parser._parse_pred('A(a)')
    CE = Parser._parse(source)
    assert search(CE, Pred) == 1.0


def test_search_time():
    import Parser
    source = "A(X):B(b)|C(X).\nB(b):."
    Pred = Parser._parse_pred('A(a)')
    b = Parser._parse_pred('B(b)')
    CE = Parser._parse(source)

    assert search(CE, b) == 1.0

    count_det = 0
    for state in CE:
        if state.determines(Pred) is not None:
            count_det += 1
            mapping = state.determines(Pred)
            new_state = state.unify(mapping[0], CE)
    assert count_det == 1
    assert new_state.solutions(CE) == True

    assert search(CE, Pred) == 1.0

def test_search_chaining_sub():
    import Parser
    source = "A(a):.\nB(X):A(X).\nC(X),D(X):A(X)."

    CE = Parser._parse(source)

    count_det = 0
    for state in CE:
        if state.determines(Parser._parse_pred('C(a)')) is not None:
            count_det += 1
            mapping = state.determines(Parser._parse_pred('C(a)'))
            new_state = state.unify(mapping[0], CE)
            #print mapping
            #print new_state

    assert search(CE, Parser._parse_pred('B(a)')) == 1.0
    assert search(CE, Parser._parse_item('!B(a)')) == 0.0
    assert search(CE, Parser._parse_pred('C(a)')) == 1.0
    assert search(CE, Parser._parse_item('!C(a)')) == 0.0
    assert search(CE, Parser._parse_pred('C(b)')) == 'Unknown'
    assert search(CE, Parser._parse_item('!C(b)')) == 'Unknown'

def test_prob_chaining():
    import Parser
    source = "A(a):.\nB(X):!A(X).\nC(a):!A(a)."

    CE = Parser._parse(source)

    assert search(CE, Parser._parse_pred('A(a)')) == 1.0
    assert search(CE, Parser._parse_pred('!A(a)')) == 0.0
    assert search(CE, Parser._parse_pred('C(a)')) == 0.0
    assert search(CE, Parser._parse_pred('!C(a)')) == 1.0
    assert search(CE, Parser._parse_pred('B(a)')) == 0.0
    assert search(CE, Parser._parse_pred('!B(a)')) == 1.0

def test_prob_chaining():
    import Parser
    source = "A(a) =| 0.5\n B(a) =| 0.5\n C(a): A(a),B(a).\nD(a):A(a).\nD(a):B(a)."

    CE = Parser._parse(source)

    assert search(CE, Parser._parse_pred('C(a)')) == 0.25
    assert search(CE, Parser._parse_pred('!C(a)')) == 0.75
    assert search(CE, Parser._parse_pred('D(a)')) == 0.75

def test_expr_search_simple():
    import Parser
    import sympy
    source = ":x=24"

    CE = Parser._parse(source)
    assert search_expr(CE, sympy.Symbol('x'))[0] == 24

def test_expr_search():
    import Parser
    import sympy
    source=":x=24\n:y=x+3\n:z=x**2+y**2"

    CE = Parser._parse(source)

    assert search_expr(CE, sympy.Symbol('x'))
    assert search_expr(CE, sympy.Symbol('y'))
    assert search_expr(CE, sympy.Symbol('z'))
    assert float(search_expr(CE, sympy.Symbol('z'))[0]) == 1305

