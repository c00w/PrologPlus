def search(CE, term):
    if search_true(CE, term):
        return True
    if search_false(CE, term):
        return False
    return 'Unknown'
    
def term_determines(item, term):
    if item in term.left:
        return True
    return False
    
def find_unify(Pred, Statement):
    return Statement.find_unify()

def search_true(CE, Pred):
    for Statement in CE:
        if term_determines(Pred, Statement):
            pred = find_unify(Pred, Statement)
            if pred is not None:
                print pred
    return False

def search_false(CE, Term):
    pass
    

def test_determinines():
    from Parser import _parse_statement, _parse_pred
    term = _parse_statement("A(X):.")
    assert term_determines(_parse_pred("A(a)"), term)
