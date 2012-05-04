from copy import deepcopy

def search(CE, term):
    if search_true(CE, term):
        return True
    term.negated = not term.negated
    if search_true(CE, term):
        return False
    return 'Unknown'
    
def find_unify(Pred, Statement):
    return Statement.find_unify()

def search_true(CE, Pred, skip = None):
    poss = []
    for Statement in CE:
        det = Statement.determines(Pred)
        if det is not None:
            for mapping in det:
                poss.append((Statement, mapping))
    
    for state, mapping in poss:
        if mapping == {}:
            if state.true(CE):
                return True
        
    for state, mapping in poss:
        if mapping != {}:
            new_state = state.unify(mapping)
            if new_state in CE:
                continue
            if new_state.true(CE):
                return True
        
    return False
    
#def test_recurse():
#    import Parser
#    source = "A(a):A(a)."
#    CE = Parser._parse(source)
#    assert search(CE, Parser._parse_pred('A(a)')) == 'Unknown'
    
def test_search():
    import Parser
    source = "A(a):."
    CE = Parser._parse(source)
    assert search(CE, Parser._parse_pred('A(a)')) == True
    
    source = "A(X):."
    CE = Parser._parse(source)
    assert search(CE, Parser._parse_pred('A(a)')) == True
    
def test_search_compl():
    import Parser
    source = "A(X):B(b).\nB(b):."
    Pred = Parser._parse_pred('A(a)')
    b = Parser._parse_pred('B(b)')
    CE = Parser._parse(source)
    
    assert search(CE, b) == True
    
    count_det = 0
    for state in CE:
        if state.determines(Pred) is not None:
            count_det += 1
            mapping = state.determines(Pred)
            new_state = state.unify(mapping[0])
    assert count_det == 1
    assert new_state.true(CE) == True
    
    assert search(CE, Pred) == True
    
def test_search_compl_neg():
    import Parser
    source = "A(X):!B(b).\n!B(b):."
    Pred = Parser._parse_pred('A(a)')
    b = Parser._parse_pred('!B(b)')
    CE = Parser._parse(source)
    
    assert search(CE, b) == True
    
    count_det = 0
    for state in CE:
        if state.determines(Pred) is not None:
            count_det += 1
            mapping = state.determines(Pred)
            new_state = state.unify(mapping[0])
    assert count_det == 1
    assert new_state.true(CE) == True
    
    assert search(CE, Pred) == True
    
def test_search_time():
    import Parser
    source = "A(X):B(b)|C(X).\nB(b):."
    Pred = Parser._parse_pred('A(a)')
    b = Parser._parse_pred('B(b)')
    CE = Parser._parse(source)
    
    assert search(CE, b) == True
    
    count_det = 0
    for state in CE:
        if state.determines(Pred) is not None:
            count_det += 1
            mapping = state.determines(Pred)
            new_state = state.unify(mapping[0])
    assert count_det == 1
    assert new_state.true(CE) == True
    
    assert search(CE, Pred) == True
    
def test_search_chaining_sub():
    import Parser
    source = "A(a):.\nB(X):A(X).\nC(X),D(X):A(X)."
    
    CE = Parser._parse(source)
    
    count_det = 0
    for state in CE:
        if state.determines(Parser._parse_pred('C(a)')) is not None:
            count_det += 1
            mapping = state.determines(Parser._parse_pred('C(a)'))
            new_state = state.unify(mapping[0])
            #print mapping
            #print new_state
    
    assert search(CE, Parser._parse_pred('B(a)')) == True
    assert search(CE, Parser._parse_pred('!B(a)')) == False
    assert search(CE, Parser._parse_pred('C(a)')) == True
    assert search(CE, Parser._parse_pred('!C(a)')) == False
    assert search(CE, Parser._parse_pred('C(b)')) == 'Unknown'
    assert search(CE, Parser._parse_pred('!C(b)')) == 'Unknown'
    
    
    
    
