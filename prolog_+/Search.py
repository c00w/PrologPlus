def search(CE, term):
    if search_true(CE, term):
        return True
    if search_false(CE, term):
        return False
    return 'Unknown'

def search_true(CE, Term):
    for item in CE:
        if item.true(Term, CE):
            return True
    return False

def search_false(CE, Term):
    pass
