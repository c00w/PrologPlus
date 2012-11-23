from copy import deepcopy
from sympy.parsing.sympy_parser import parse_expr
from sympy.solvers import solve

def isvariable(item):
    """
    Returns whether a name is a variable
    """
    assert len(item) > 0
    if item[0] == '!':
        assert len(item) > 1
        return item[1].upper() == item[1]
    return item[0].upper() == item[0]

class Variable():
    def __init__(self, name):
        assert isvariable(name)
        self.name = name

    def unify(self, mapping, CE):
        if self in mapping:
            return deepcopy(mapping[self])
        return deepcopy(self)

    def __eq__(self, other):
        return type(self) == type(other) and self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return 'Variable("' + self.name + '")'

    def __hash__(self):
        return hash(self.name) + hash('VARIABLE')

class Disjunction():
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def set_prob(self, b):
        pass

    def determines(self, other):
        return None

    def unify(self, mapping, CE):
        new_self = deepcopy(self)
        new_self.left = self.left.unify(mapping, CE)
        new_self.right = self.right.unify(mapping, CE)
        return new_self

    def solutions(self, CE, mapping):
        val, nmapping = self.left.solutions(CE, mapping)
        if val == True:
            return True, nmapping

        val, mapping = self.right.solutions(CE, mapping)

        return val, mapping

    def prob(self, item=None):
        if item == None:
            return self.right.prob() + self.left.prob() - self.right.prob()*self.left.prob()
        assert item == self
        return self.prob()

    def __eq__(self, other):
        if other is None:
            return False
        return type(self) == type(other) and self.left == other.left and self.right == other.right

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return 'Disjunction(' + str(self.left) + ", " + str(self.right) + ')'

    def __hash__(self):
        return hash(self.left) + hash(self.right) + hash('DISJUNCTION::')

class Conjunction():
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def set_prob(self, p):
        pass

    def determines(self, other):
        pass
        left = self.left.determines(other)
        right = self.right.determines(other)
        if left == None and right == None:
            return None
        value = []
        if left is not None:
            value.extend(left)
        if right is not None:
            value.extend(right)
        return value

    def unify(self, mapping, CE):
        new_self = deepcopy(self)
        new_self.left = self.left.unify(mapping, CE)
        new_self.right = self.right.unify(mapping, CE)
        return new_self

    def solutions(self, CE, mapping):
        val, mapping = self.left.solutions(CE, mapping)
        if val != True:
            return False, mapping
        val, mapping = self.right.solutions(CE, mapping)
        return val, mapping

    def prob(self, item=None):
        if item == None:
            return self.left.prob() * self.right.prob()
        if self.left.determines(item):
            return self.left.prob()
        elif self.right.determines(item):
            return self.right.prob()
        assert item == self
        return self.prob()

    def __eq__(self, other):
        if other is None:
            return False
        if type(self) != type(other):
            return False
        return type(self) == type(other) and self.left == other.left and self.right == other.right


    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return 'Conjunction(' + str(self.left) + ', ' + str(self.right)  + ')'

    def __hash__(self):
        return hash(self.left) + hash(self.right) + hash('CONJUNCTION::')

class Negation():
    def __init__(self, child):
        self.child = child
        self.name = self.child.name

    def determines(self, other):
        return self.child.determines(other)

    def unify(self, mapping, CE):
        new_self = deepcopy(self)
        new_self.child = self.child.unify(mapping, CE)
        return new_self

    def solutions(self, CE, mapping):
        return self.child.solutions(CE, mapping)

    def set_prob(self, p):
        self.child.set_prob(1-p)

    def prob(self, item=None):
        if item == None:
            return 1- self.child.prob()
        elif item == self:
            return self.prob()
        else:
            return self.child.prob(item)

    def __eq__(self, other):
        if other is None:
            return False
        return type(self) == type(other) and self.child == other.child

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return 'Negation(' + str(self.child) + ', p=' + str(self.prob()) + ')'

    def __hash__(self):
        return hash(self.child) + hash('Negation')


class Statement():
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def determines(self, item):
        while isinstance(item, Negation):
            item = item.child
        return self.left.determines(item)

    def update_prob(self):
        if self.right:
            self.left.set_prob(self.right.prob())

    def __repr__(self):
        return '<Statement ' + str(self.left) + ':' + str(self.right) + ' >'

    def __hash__(self):
        return hash(self.left) + hash(self.right)

    def unify(self, mapping, CE):
        new_self = deepcopy(self)
        new_self.left = self.left.unify(mapping, CE)
        if self.right is not None:
            new_self.right = self.right.unify(mapping, CE)
            new_self.update_prob()
        return new_self

    def solutions(self, CE):
        if self.right == None:
            return True

        val, mapping = self.right.solutions(CE, [{}])
        return val

    def prob(self, item=None):
        return self.left.prob(item)

    def __eq__(self, other):
        return self.left == other.left and self.right == other.right

    def __ne__(self, other):
        return not self.__eq__(other)

import Search

class Predicate():
    def __init__(self, name, args, prob=1.):
        self.name = name
        self.args = args
        self.probability = prob

    def set_prob(self, p):
        self.probability = p

    def prob(self, item=None):
        if item == None:
            return self.probability
        assert isinstance(item, Predicate) 
        assert self.determines(item)
        return self.probability

    def hasVariables(self):
        for item in self.args:
            if isinstance(item, Variable):
                return True

        return False

    def unify(self, mapping, CE):
        new_self = deepcopy(self)
        assert new_self == self
        for i in range(len(self.args)):
            new_self.args[i] = self.args[i].unify(mapping, CE)
        return new_self


    def solutions(self, CE, mapping_list):
        assert len(mapping_list) >0

        nmapping_list = []
        for mapping in mapping_list:
            new_self = deepcopy(self)
            assert new_self == self
            for i in range(len(self.args)):
                new_self.args[i] = self.args[i].unify(mapping, CE)

            #print 'Searching for %s' % self
            if len(Search.determination_list(CE, new_self)) == 0:
                continue


            if Search.search_solutions(CE, self) is not None:
                self.probability = 0.0
                for prob, nmapping_uf in Search.search_solutions(CE, self):
                    nmapping = {}
                    for a,b in nmapping_uf.items():
                        #print a,b
                        if isinstance(a, Atom):
                            nmapping[b]=a
                        else:
                            nmapping[a]=b

                    nmapping_list.append(dict(mapping.items() + nmapping.items()))
                    self.probability = self.probability + prob - self.probability*prob
        #print self, mapping_list, nmapping_list
        return len(nmapping_list) > 0, nmapping_list

    def determines(self, other):
        if other is None:
            return None

        if self.name != other.name:
            return None

        if len(self.args) != len(other.args):
            return None

        mapping = {}
        for i in range(len(self.args)):

            if self.args[i] != other.args[i] and not isinstance(self.args[i], Variable) and not isinstance(other.args[i], Variable):
                return None
            if self.args[i] != other.args[i]:
                mapping[self.args[i]] = other.args[i]
        return [mapping]

    def __repr__(self):
        return 'Predicate(' + self.name +', ' + ', '.join(map(str, self.args)) + 'P=' + str(self.probability) + ')'

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, Predicate):
            return False
        return type(self) == type(other) and self.name == other.name and self.args == other.args

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name) + sum(map(hash, self.args)) + hash('PREDICATE')

class Atom(Predicate):
    def __init__(self, name, prob = 1.):
        assert not isvariable(name)
        self.name = name
        self.args = []
        self.probability = prob

    def __eq__(self, other):
        if other is None:
            return False
        return type(self) == type(other) and self.name == other.name and self.args == other.args

    def unify(self, mapping, CE):
        new = deepcopy(self)
        assert new == self
        return new

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return 'Atom("' + self.name + '")'

def test_determines():
    import Parser
    source = "A(a):."
    CE = Parser._parse(source)
    for state in CE:
        assert state.determines(Parser._parse_pred('A(a)')) == [{}]

def test_unify():
    import Parser
    source = "A(X):."
    CE = Parser._parse(source)
    for state in CE:
        mapping = state.determines(Parser._parse_pred('A(a)'))
        assert len(mapping) > 0
        for item in mapping:
            assert state.unify(item, CE) != state

def test_statement_set_membership():
    import Parser
    source = "A(a):A(a)."
    CE = Parser._parse(source)
    state = Parser._parse_statement("A(a):A(a).")
    assert state in CE

def test_unify_big():
    import Parser
    source = "A(X):."
    CE = Parser._parse(source)
    for state in CE:
        assert str(state.unify({Variable("X"):Atom("a")}, CE)) != str(state)

def test_hasVariables():
    import Parser
    pred = "A(X,a,b,c)"
    predf = "A(a,d,e)"
    pred = Parser._parse_pred(pred)
    predf = Parser._parse_pred(predf)
    assert pred.hasVariables() == True
    assert predf.hasVariables() == False

class Equation():

    def __init__(self, equation):
        #If there is an equal sign in the equation do some basic fudgng
        if '=' in equation:
            equation = equation.split('=', 1)[1] + '-' + equation.split('=', 1)[0]
        self.equation = parse_expr(equation)
    def __eq__(self, other):
        return self.equation == other.equation

    def __hash__(self):
        return hash(self.equation)

    def determines(self, other):
        if self.equation.has(other):
            return self.equation.subs(other, 0).free_symbols

    def solve(self, variable, CE):
        mapping = {}
        for var in self.determines(variable):
            search_result = Search.search_expr(CE, var)
            if search_result is not None and len(search_result):
                mapping[var] = search_result[0]
            else:
                break
        if len(mapping) != len(self.determines(variable)):
            return None

        new_eqn = self.equation
        while len(new_eqn.free_symbols)> 1:
            for var, value in mapping.iteritems():
                new_eqn = new_eqn.subs(var, value)

        return solve(new_eqn, variable, dict=False)

def test_equation():
    a = Equation('x+y**2-1')
    assert len(a.determines('x')) == 1

def test_solve():
    a = parse_expr('x-y-24')
    a = a.subs('x', 24)
    assert solve(a, 'y') == [0]
