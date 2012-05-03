from copy import copy
import Search

def isvariable(item):
    """
    Returns whether a name is a variable
    """
    assert len(item) > 0
    if item[0] == '!':
        assert len(item) > 1
        return item[1].upper() == item[1]
    return item[0].upper() == item[0]
    
class Atom():
    def __init__(self, name):
        assert not isvariable(name)
        self.name = name
    
    def __eq__(self, other):
        return self.name == other.name
        
    def __repr__(self):
        return 'Atom("' + self.name + '")'
    
    def __hash__(self):
        return hash(self.name) + hash('Variable')
        
    def unbound(self, head):
        return head
        
class Variable():
    def __init__(self, name):
        assert isvariable(name)
        self.name = name
    
    def __eq__(self, other):
        return self.name == other.name
        
    def __repr__(self):
        return 'Variable("' + self.name + '")'
    
    def __hash__(self):
        return hash(self.name) + hash('VARIABLE')
        
    def unbound(self, head):
        head.add(self)
        return head
        
def Term(item):
    if isvariable(item):
        return Variable(item)
    return Atom(item)

class Predicate():
    def __init__(self, predicate):
        if '(' not in predicate:
            raise ValueError('Invalid Form')
        if ')' not in predicate:
            raise ValueError('Invalid Form')
        
        self.Pname = predicate[:predicate.find('(')]
        argsterm = predicate[predicate.find('(')+1:predicate.find(')')]
        self.args = map(Term,argsterm.split(','))
        
    def __contains__(self, other):
        if other == None:
            return False
        return self == other
        
    def unbound(self, head):
        assert head != None
        for item in self.args:
            head = item.unbound(head)
            assert head != None
        return head
        
    def __repr__(self):
        return '<Predicate ' + self.Pname + ' ' + ', '.join(map(str, self.args)) + ' >'
        
    def unify(self, variable, value):
        """
        Unifies a variable to a value and returns a new value
        """
        if variable not in self.args:
            return self
        
        new = copy(self)
        
        new_args = copy(self.args)
        while variable in new_args:
            new_args[new_args.index(variable)] = value
        
        new.args = new_args
        
        assert new_args != self.args
        
        return new
        
    def __eq__(self, other):
        if other == None:
            return False
        return self.Pname == other.Pname and self.args == other.args
        
    def __hash__(self):
        return hash(self.Pname) + sum(map(hash, self.args))
        
    def true(self, CE):
        return Search.search_true(CE, self)
        
        
class Conjunction():
    def __init__(self, conjunction):
        assert ',' in conjunction
        first = conjunction[:conjunction.index(',')]
        second = conjunction[conjunction.index(',')+1:]
        self.item = Predicate(first)
        self.tail = Predicate(second) if len(second) > 0 else None
        
    def __contains__(self, other):
        return self.item == other or other in self.tail if self.tail else False
        
    def __eq__(self, other):
        if other == None:
            return False
        return self.item == other.item and self.tail == other.tail
        
    def __repr__(self):
        return '<Conjunction ' + str(self.item) + ' ' + str(self.tail)  + ' >'
        
    def true(self, CE):
        return self.item.true(CE) and self.tail.true(CE) if self.tail else True
        
    def false(self, CE):
        return self.item.false(CE) and self.tail.false(CE) if self.tail else True
        
    def __hash__(self):
        return hash(self.item) + hash(self.tail)
        
    def unbound(self, head):
        assert head != None
        head = self.item.unbound(head)
        assert head != None
        head = self.tail.unbound(head) if self.tail else head
        assert head != None
        return head
        
    def unify(self, variable, atom):
        new = copy(self)
        new.head = self.item.unify(variable, atom)
        new.tail = self.tail.unify(variable, atom) if self.tail else None
        return new
        
class Statement():
    def __init__(self, item):
        assert ':' in item
        lh, rh = item.split(':',1)
        if ',' in lh:
            self.left = Conjunction(lh)
        else:
            self.left = Predicate(lh)
        
        if rh == '.' or rh == '':
            self.right = None
        elif ',' in rh:
            self.right = Conjunction(rh)
        else:
            self.right = Predicate(rh)
            
    def unbound(self, head):
        assert head != None
        head = self.left.unbound(head)
        assert head != None
        head = self.right.unbound(head) if self.right else head
        assert head != None
        return head

    def __repr__(self):
        return '<Statement ' + str(self.left) + ' ' + str(self.right) + ' >'
        
    def __contains__(self, item):
        return item in self.left
        
    def unify(self, variable, atom):
        new = copy(self)
        new.left = self.left.unify(variable, atom)
        new.right = self.right.unify(variable, atom) if self.right else None
        return new
        
    def true(self, item, CE):
        mappings = {}
        new_CE = copy(CE)
        if self in new_CE:
            new_CE.remove(self)
        
        def left_true(item):
            if item.right == None or item.right.true(new_CE):
                return True
                
            #See if we can bind it
            unbound_right = item.right.unbound(set())
            if len(unbound_right) > 0:
                raise ValueError("NOT IMPLEMENTED")
        
        #Check if we can satisfy this without doing unification
        if item in self.left:
            if left_true(self):
                return True
                
        else:
            #Try binding each value to what we want to find and see if it works
            unbound = self.left.unbound(set())
            for variable in unbound:
                if len(item.args) == 1:
                    new = self.unify(variable, item.args[0])
                    if item in new.left:
                        if left_true(new):
                            return True
                        
                else:
                    raise ValueError("Not implemented")
            
        #Ok, figure out what we can bind
        unbound = self.unbound(set())
        if len(unbound) == 0:
            return False
         
                
        return False
        
    def __hash__(self):
        return hash(self.left) + hash(self.right)
        
# PY.TEST tests
    

def test_Statement():
    test = ['A(b):.','A(X):B(X),C(X)', 'A(X),B(X):C(X),D(d)']
    for state in test:
        assert Statement(state)
    
def test_True():
    CE = set()
    CE.add( Statement('A(b):.'))
    CE.add(Statement('A(c):A(b)'))
    assert Statement('A(b):.').true(Predicate('A(b)'), CE)
    assert Statement('A(c):A(b)').true(Predicate('A(c)'), CE)
    
def test_unify():
    test_pred = Predicate('A(X)')
    new = test_pred.unify(Variable('X'), Atom('a'))
    assert new.args[0] == Atom('a')

    test_stat = Statement('A(X):.')
    new = test_stat.unify(Variable('X'), Atom('a'))
    assert new.left.args[0] == Atom('a')
    assert new.true(Predicate('A(a)'), set())

    CE = set()
    CE.add( Statement('A(b):.'))
    CE.add(Statement('A(X):A(b)'))
    assert Search.search_true(CE, Predicate('A(c)'))
    
def test_search():
    CE = set()
    CE.add( Statement('A(b):.'))
    CE.add(Statement('A(c):A(b)'))
    assert Search.search_true(CE, Predicate('A(c)'))
    
        
def test_Predicate():
    test = 'A(X,b,c)'
    pred = Predicate(test)
    assert len(pred.args) == 3
    assert pred.unify(Variable('X'),Atom('a')) != pred
    
