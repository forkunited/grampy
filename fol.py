import data
import random
import nltk
from nltk.sem.logic import *
import copy

class RandomModel:
    def __init__(self, domain, properties, binary_rels):
        self._domain = domain
        self._properties = properties
        self._binary_rels = binary_rels

        property_sets = [set([]) for i in range(len(properties))]
        binary_rel_sets = [set([]) for i in range(len(binary_rels))]

        v = []
        for i in range(len(domain)):
            v.append((domain[i], domain[i])) 
            
            for j in range(len(properties)):
                if random.randint(0,1) == 1:
                    property_sets[j].add(domain[i])
            
            for j in range(len(binary_rels)):
                for k in range(len(domain)):
                    binary_rel_sets[j].add((domain[i], domain[k]))

        for i in range(len(property_sets)):
            v.append((properties[i], property_sets[i]))

        for i in range(len(binary_rel_sets)):
            v.append((binary_rels[i], binary_rel_sets[i]))

        val = nltk.Valuation(v)
        self._model = nltk.Model(set(domain), val)

    def evaluate(self, form, g):
        return self._model.evaluate(form, g)

class Datum:
    def __init__(self, model):
        self._model = model

    def get_label(self):
        return self._label
   
    def get_model(self):
        return self._model

    @staticmethod
    def make_random(domain, properties, binary_rels, label_fn):
        m = RandomModel(domain, properties, binary_rels)
        d = Datum(m)
        d._label = label_fn(d)
        return d


class DataSet(data.DataSet):
    def __init__(self):
        data.DataSet.__init__(self)

    @staticmethod
    def make_random(size, domain, properties, binary_rels, label_fn, seed=1):
        random.seed(seed)
        D = DataSet()
        for i in range(0, size):
            D._data.append(Datum.make_random(domain, properties, binary_rels, label_fn))
        return D

class ClosedFormula:
    def __init__(self, form, g):
        self._form = form
        self._g = g

    def get_g(self):
        return self._g

    def get_form(self):
        return self._form

    def get_exp(self, close=False, exclude=[]):
        exp = nltk.sem.Expression.fromstring(self._form)
        if not close:
            return exp
        for key in self._g:
            if key not in exclude:
                key_exp = nltk.sem.Expression.fromstring(key)
                value_exp = nltk.sem.Expression.fromstring(value)
                exp = exp.replace(key.variable, value, False)
        return exp


    def exp_matches(self, closed_form):
        return self.get_exp().equiv(closed_form.get_exp())

    def is_sub_g(self, closed_form):
        for v in self._g:
            f_g = closed_form.get_g()
            if v not in f_g or f_g[v] != self._g[v]:
                return False
        return True
    
    def matches(self, closed_form):
        return self.exp_matches(closed_form) and self.is_sub_g(closed_form)

    def orthogonize(self, closed_form):
        new_exp = self.get_exp()
        new_g = []
        for v in self._g:
            if v in closed_form.get_g():
                v_new = v
                while v_new in closed_form.get_g():
                    v_new = v_new + '1'
                v_exp = nltk.sem.Expression.fromstring(v)
                v_new_exp = nltk.sem.Expression.fromstring(v_new)
                new_exp = new_exp.replace(v_exp.variable, v_new_exp, False)
                new_g.append((v_new, self._g[v]))
            else:
                new_g.append((v, self._g[v]))
        return ClosedFormula(str(new_exp), nltk.Assignment(self._g.domain, new_g))


class OpenFormula:
    def __init__(self, domain, form, variables, init_g={}):
        self._domain = domain
        self._form = form
        self._variables = variables
        self._init_g = init_g
        self._closed_forms = self._make_closed_forms(domain, form, variables, init_g)

        
    def _make_closed_forms(self, domain, form, variables, init_g):
        assgn_lists = self._make_assignments_helper(domain, variables, init_g, 0, [[]])
        closed = []
        for i in range(len(assgn_lists)):
            g = nltk.Assignment(domain, assgn_lists[i])
            closed.append(ClosedFormula(form, g))
        return closed

    def _make_assignments_helper(self, domain, variables, init_g, i, assgn_lists):
        if (i == len(variables)):
            return assgn_lists
        next_lists = []

        if variables[i] not in init_g:
            for j in range(len(domain)):
                for k in range(len(assgn_lists)):
                    assgn_list = copy.deepcopy(assgn_lists[k])
                    assgn_list.append((variables[i], domain[j]))        
                    next_lists.append(assgn_list)
        else:
            for k in range(len(assgn_lists)):
                assgn_list = copy.deepcopy(assgn_lists[k])
                assgn_list.append((variables[i], init_g[variables[i]]))
                next_lists.append(assgn_list)

        return self._make_assignments_helper(domain, variables, init_g, i+1, next_lists)

    def exp_matches(self, open_form):
        return self.get_exp().equiv(open_form.get_exp())

    def get_form(self):
        return self._form

    def get_exp(self):
        return nltk.sem.Expression.fromstring(self._form)

    def get_closed_forms(self):
        return self._closed_forms


class FeatureToken(data.FeatureToken):
    def __init__(self, closed_form):
        data.FeatureToken.__init__(self)
        self._closed_form = closed_form

    def get_closed_form(self):
        return self._closed_form


class FeatureType(data.FeatureType):
    def __init__(self, open_form):
        data.FeatureType.__init__(self)
        self._open_form = open_form

    def get_open_form(self):
        return self._open_form

    def compute(self, datum):
        closed_forms = self._open_form.get_closed_forms()
        expr = self._open_form.get_form()
        return [1.0 if datum.get_model().evaluate(expr, c.get_g()) else 0.0 for c in closed_forms]

    def get_size(self):
        return len(self._open_form.get_closed_forms())

    def get_token(self, index):
        return FeatureToken(self._open_form.get_closed_forms()[index])

    def equals(self, feature_type):
        return self._open_form.exp_matches(feature_type.get_open_form())


class UnaryRule(data.UnaryRule):
    def __init__(self, lhs_closed_form, rhs_open_form_fn):
        data.UnaryRule.__init__(self)
        self._lhs_closed_form = lhs_closed_form
        self._rhs_open_form_fn = rhs_open_form_fn
    
    def matches(self, feature_token):
        if self._lhs_closed_form is None:
            return True
        f_form = feature_token.get_closed_form()

        if not self._lhs_closed_form.matches(f_form):
            return False

        return True 

    def apply(self, feature_token):
        if not self.matches(feature_token):
            return None
        open_forms = self._rhs_open_form_fn(feature_token.get_closed_form())
        return [FeatureType(open_form) for open_form in open_forms]


class BinaryRule(data.BinaryRule):
    def __init__(self, lhs_closed_form1, lhs_closed_form2, rhs_open_form_fn, ordered=False):
        data.BinaryRule.__init__(self)
        self._lhs_closed_form1 = lhs_closed_form1
        self._lhs_closed_form2 = lhs_closed_form2
        self._rhs_open_form_fn = rhs_open_form_fn
        self._ordered = ordered

    def matches(self, feature_token1, feature_token2):
        if self._lhs_closed_form1 is None and self._lhs_closed_form2 is None:
            return True

        f_form1 = feature_token1.get_closed_form()
        f_form2 = feature_token2.get_closed_form()
        if self._lhs_closed_form1.matches(f_form1) and self._lhs_closed_form2.matches(f_form2):
            return True
        if not self._ordered and self._lhs_closed_form1.matches(f_form2) and self._lhs_closed_form2.matches(f_form1):
            return True
        return False

    def apply(self, feature_token1, feature_token2):
        if not self.matches(feature_token1, feature_token2):
            return None
        open_forms = self._rhs_open_form_fn(feature_token1.get_closed_form(), feature_token2.get_closed_form())
        return [FeatureType(open_form) for open_form in open_forms]

