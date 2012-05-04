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
    
class Predicate():
    def __init__(self, name, args):
        self.name = name
        self.args = args
        
    def __contains__(self, other):
        if other is None:
            return False
        if other in self.args:
            return True
            
        self.arity = len(self.args)
        other.arity = len(other.args)
        if self.arity != other.arity:
            return False
        for i in range(self.arity):
            if self.args[i] != other.args[i] and not isinstance(self.args[i], Variable) and not isinstance(other.args[i], Variable):
                return False
        return True
                
        
    def __repr__(self):
        return 'Predicate(' + self.name +', ' + ', '.join(map(str, self.args)) + ')'
        
    def __eq__(self, other):
        if other is None:
            return False
        return type(self) == type(other) and self.name == other.name and self.args == other.args
        
    def __hash__(self):
        return hash(self.name) + sum(map(hash, self.args)) + hash('PREDICATE')
    
class Atom(Predicate):
    def __init__(self, name):
        assert not isvariable(name)
        self.name = name
        self.args = []
        
    def __repr__(self):
        return 'Atom("' + self.name + '")'
        
class Variable():
    def __init__(self, name):
        assert isvariable(name)
        self.name = name
    
    def __eq__(self, other):
        return type(self) == type(other) and self.name == other.name
        
    def __repr__(self):
        return 'Variable("' + self.name + '")'
    
    def __hash__(self):
        return hash(self.name) + hash('VARIABLE')
        
class Disjunction():
    def __init__(self, left, right):
        self.left = left
        self.right = right
        
    def __contains__(self, other):
        return other in self.left or other in self.right
    
    def __eq__(self, other):
        if other is None:
            return False
        return type(self) == type(other) and self.left == other.left and self.right == other.right
        
    def __repr__(self):
        return 'Disjunction(' + str(self.left) + ", " + str(self.right) + ')'
        
    def __hash__(self):
        return hash(self.left) + hash(self.right) + hash('DISJUNCTION::')
        
class Conjunction():
    def __init__(self, left, right):
        self.item = left
        self.tail = right
        
    def __contains__(self, other):
        return other in self.item or other in self.tail
        
    def __eq__(self, other):
        if other is None:
            return False
        return self.item == other.item and self.tail == other.tail
        
    def __repr__(self):
        return 'Conjunction(' + str(self.item) + ', ' + str(self.tail)  + ')'
        
    def __hash__(self):
        return hash(self.item) + hash(self.tail) + hash('CONJUNCTION::')
        
class Statement():
    def __init__(self, left, right):
        self.left = left
        self.right = right
            
    def __contains__(self, item):
        return item in self.left
            
    def unbound(self, head):
        assert head != None
        head = self.left.unbound(head)
        assert head != None
        head = self.right.unbound(head) if self.right else head
        assert head != None
        return head

    def __repr__(self):
        return '<Statement ' + str(self.left) + ':' + str(self.right) + ' >'
        
    def __hash__(self):
        return hash(self.left) + hash(self.right)
        

    
