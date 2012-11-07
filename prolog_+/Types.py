from copy import copy, deepcopy
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
    def __init__(self, name, args, prob=1.):
        name = name.replace('!!','')
        if name[0] == '!':
            name = name[1:]
            self.negated = True
        else:
            self.negated = False
        self.name = name
        self.args = args
        self.probability = prob

    def prob(self):
        return self.probability

    def hasVariables(self):
        for item in self.args:
            if isinstance(item, Variable):
                return True

        return False

    def unify(self, mapping):

        new_self = deepcopy(self)
        assert new_self == self
        for i in range(len(self.args)):
            new_self.args[i] = self.args[i].unify(mapping)
        return new_self


    def true(self, CE, mapping_list):
        assert len(mapping_list) >0

        nmapping_list = []
        for mapping in mapping_list:
            new_self = deepcopy(self)
            assert new_self == self
            for i in range(len(self.args)):
                new_self.args[i] = self.args[i].unify(mapping)

            #print 'Searching for %s' % self
            if len(Search.determination_list(CE, new_self)) == 0:
                continue

            if Search.search_true(CE, self) is not None:
                nmapping_uf = Search.search_true(CE, self, return_mapping=True)
                nmapping = {}
                for a,b in nmapping_uf.items():
                    #print a,b
                    if isinstance(a, Atom):
                        nmapping[b]=a
                    else:
                        nmapping[a]=b

                nmapping_list.append(dict(mapping.items() + nmapping.items()))
        #print self, mapping_list, nmapping_list
        return len(nmapping_list) > 0, nmapping_list

    def determines(self, other):
        if other is None:
            return None

        if self.name != other.name:
            return None

        if len(self.args) != len(other.args):
            return None

        if self.negated != other.negated:
            return None

        mapping = {}
        for i in range(len(self.args)):

            if self.args[i] != other.args[i] and not isinstance(self.args[i], Variable) and not isinstance(other.args[i], Variable):
                return None
            if self.args[i] != other.args[i]:
                mapping[self.args[i]] = other.args[i]
        return [mapping]


    def __repr__(self):
        return 'Predicate(' + self.name +', ' + ', '.join(map(str, self.args)) + ')'

    def __eq__(self, other):
        if other is None:
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

    def unify(self, mapping):
        new = deepcopy(self)
        assert new == self
        return new

    def prob(self):
        return self.probability

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return 'Atom("' + self.name + '")'

class Variable():
    def __init__(self, name):
        assert isvariable(name)
        self.name = name

    def unify(self, mapping):
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

    def determines(self, other):
        return None

    def unify(self, mapping):
        new_self = deepcopy(self)
        new_self.left = self.left.unify(mapping)
        new_self.right = self.right.unify(mapping)
        return new_self

    def true(self, CE, mapping):
        val, nmapping = self.left.true(CE, mapping)
        if val == True:
            return True, nmapping

        val, mapping = self.right.true(CE, mapping)

        return val, mapping

    def prob(self):
        return self.right.prob() + self.left.prob() - self.right.prob()*self.left.prob()

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

    def determines(self, other):
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

    def unify(self, mapping):
        new_self = deepcopy(self)
        new_self.left = self.left.unify(mapping)
        new_self.right = self.right.unify(mapping)
        return new_self

    def true(self, CE, mapping):
        val, mapping = self.left.true(CE, mapping)
        if val != True:
            return False, mapping
        val, mapping = self.right.true(CE, mapping)
        return val, mapping

    def prob(self):
        return self.left.prob() * self.right.prob()

    def __eq__(self, other):
        if other is None:
            return False
        return type(self) == type(other) and self.left == other.left and self.right == other.right


    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return 'Conjunction(' + str(self.left) + ', ' + str(self.right)  + ')'

    def __hash__(self):
        return hash(self.left) + hash(self.right) + hash('CONJUNCTION::')

class Statement():
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def determines(self, item):
        return self.left.determines(item)

    def __repr__(self):
        return '<Statement ' + str(self.left) + ':' + str(self.right) + ' >'

    def __hash__(self):
        return hash(self.left) + hash(self.right)

    def unify(self, mapping):
        new_self = deepcopy(self)
        new_self.left = self.left.unify(mapping)
        if self.right is not None:
            new_self.right = self.right.unify(mapping)
        return new_self

    def true(self, CE):
        if self.right == None:
            return True

        val, mapping = self.right.true(CE, [{}])
        return val

    def __eq__(self, other):
        return self.left == other.left and self.right == other.right

    def __ne_(self, other):
        return not self.__eq__(self, other)

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
            assert state.unify(item) != state

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
        assert str(state.unify({Variable("X"):Atom("a")})) != str(state)

def test_hasVariables():
    import Parser
    pred = "A(X,a,b,c)"
    predf = "A(a,d,e)"
    pred = Parser._parse_pred(pred)
    predf = Parser._parse_pred(predf)
    assert pred.hasVariables() == True
    assert predf.hasVariables() == False

