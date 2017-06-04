import random
import nltk
import numpy as np
from nltk.sem.logic import *
import copy

class RelationalModel:
    def __init__(self, domain, properties, binary_rels, valuation):
        self._domain = domain
        self._properties = properties
        self._binary_rels = binary_rels
        self._model = nltk.Model(set(domain), nltk.Valuation(valuation))

    def evaluate(self, form, g):
        return self._model.evaluate(form, g)

    def satisfiers(self, form, var, g):
        return self._model.satisfiers(nltk.sem.Expression.fromstring(form), var, g)

    def satisfiers_exp(self, expr, var, g):
        return self._model.satisfiers(expr, var, g)

    @staticmethod
    def make_random(domain, properties, binary_rels):
        property_sets = [set([]) for i in range(len(properties))]
        binary_rel_sets = [set([]) for i in range(len(binary_rels))]

        v = []
        for i in range(len(domain)):
            v.append((domain[i], domain[i])) 
            
            for j in range(len(properties)):
                if np.random.randint(2) == 1:
                    property_sets[j].add(domain[i])
            
            for j in range(len(binary_rels)):
                for k in range(len(domain)):
                    if np.random.randint(2) == 1:
                        binary_rel_sets[j].add((domain[i], domain[k]))

        for i in range(len(property_sets)):
            v.append((properties[i], property_sets[i]))

        for i in range(len(binary_rel_sets)):
            v.append((binary_rels[i], binary_rel_sets[i]))

        return RelationalModel(domain, properties, binary_rels, v)


class ClosedFormula:
    def __init__(self, form, g):
        self._exp = None
        self._form = form
        self._g = g

    def get_g(self):
        return self._g

    def get_form(self):
        return self._form

    def get_exp(self, close=False, exclude=[]):
        if self._exp is None:
            self._exp = nltk.sem.Expression.fromstring(self._form)
        exp = self._exp

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

    def __str__(self):
        new_exp = self.get_exp()
        for v in self._g:
            v_exp = nltk.sem.Expression.fromstring(v)
            value_exp = nltk.sem.Expression.fromstring(self._g[v])
            new_exp = new_exp.replace(v_exp.variable, value_exp, False)
        return str(new_exp)

    def conjoin(self, cf2, orthogonize=False):
        if orthogonize:
            cf2 = cf2.orthogonize(self)
        new_g = of2_o.get_g().copy()
        new_g.update(self.get_g())
        return ClosedFormula(str(self.get_exp() & of2.get_exp()), new_g)

    def disjoin(self, cf2, orthogonize=False):
        if orthogonize:
            cf2 = cf2.orthogonize(self)
        new_g = of2_o.get_g().copy()
        new_g.update(self.get_g())
        return ClosedFormula(str(self.get_exp() | of2.get_exp()), new_g)

    def negate(self):
        return ClosedFormula(str(- self.get_exp()), self.get_g())

    def is_unary_predicate(self):
        return isinstance(self.get_exp(), nltk.sem.logic.ApplicationExpression) and (len(self.get_exp().free()) + len(self.get_exp().constants())) == 1

    def get_predicates(self):
        return [str(pred) for pred in self.get_exp().predicates()]


class OpenFormula:
    def __init__(self, domain, form, variables, init_g=None):
        self._exp = None
        self._domain = domain
        self._form = form
        self._variables = variables
        if init_g is not None:
            self._init_g = init_g
        else:
            self._init_g = nltk.Assignment(self._domain, [])
        self._closed_forms = None

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

    def get_variables(self):
        return self._variables

    def get_init_g(self):
        return self._init_g

    def exp_matches(self, open_form):
        return self.get_exp().equiv(open_form.get_exp())

    def get_form(self):
        return self._form

    def get_exp(self):
        if self._exp is None:
            self._exp = nltk.sem.Expression.fromstring(self._form)
        return self._exp

    def get_closed_forms(self):
        if self._closed_forms is None:
            self._closed_forms = self._make_closed_forms(self._domain, self._form, self._variables, init_g)
        return self._closed_forms

    def orthogonize(self, open_form):
        new_exp = self.get_exp()
        new_g = []
        new_variables = []
        for v in self._variables:
            if v in open_form._variables:
                v_new = v
                while v_new in open_form._variables:
                    v_new = v_new + '1'
                v_exp = nltk.sem.Expression.fromstring(v)
                v_new_exp = nltk.sem.Expression.fromstring(v_new)
                new_exp = new_exp.replace(v_exp.variable, v_new_exp, False)
                if v in self._init_g:
                    new_g.append((v_new, self._init_g[v]))

                new_variables.append(v_new)
            elif v in self._init_g:
                new_g.append((v, self._init_g[v]))
                new_variables.append(v)
            else:
                new_variables.append(v)
        return OpenFormula(self._domain, str(new_exp), new_variables, nltk.Assignment(self._init_g.domain, new_g))

    # FIXME Note that for now this assumes that self and of2 have the same domain
    def conjoin(self, of2, orthogonize=False):
        if orthogonize:
            of2 = of2.orthogonize(self)
        new_init_g = of2.get_init_g().copy()
        new_init_g.update(self.get_init_g())
        new_variables = list(set(self._variables + of2._variables))
 
        return OpenFormula(self._domain, str(self.get_exp() & of2.get_exp()), new_variables, init_g=new_init_g)


    def disjoin(self, of2, orthogonize=False):
        if orthogonize:
            of2 = of2.orthogonize(self)
        new_init_g = of2_o.get_init_g().copy()
        new_init_g.update(self.get_init_g())
        new_variables = list(set(self._variables + of2._variables))

        return OpenFormula(self._domain, str(self.get_exp() | of2.get_exp()), new_variables, init_g=new_init_g)

    def negate(self):
        return OpenFormula(self._domain, str(- self._get_exp()), self._variables, self._init_g)

    def _satisfiers_helper(self, model, variables, var_exprs, var_index, partial_g):
        if var_index == len(self._variables):
             return [nltk.Assignment(self._domain, partial_g)]

        sats = []
        var = variables[var_index]
        expr = var_exprs[var_index]
        var_sats = model.satisfiers_exp(expr, var, nltk.Assignment(self._domain, partial_g))

        for var_sat in var_sats:
            partial_g_next = copy.deepcopy(partial_g)
            partial_g_next.append((var, var_sat))
            sats.extend(self._satisfiers_helper(model, variables, var_exprs, var_index + 1, partial_g_next))

        return sats

    def satisfiers(self, model):
        variables = []
        partial_g = []
        var_exprs = []
        for i in range(len(self._variables)):
            var = self._variables[i]
            if var not in self._init_g:
                exist_str_i = ""
                for j in range(i+1, len(self._variables)):
                    exist_str_i += "exists " + self._variables[j] + "."
                var_exprs.append(nltk.sem.Expression.fromstring(exist_str_i + self._form))
                variables.append(var)
            else:
                partial_g.append((var, self._init_g[var]))

        return self._satisfiers_helper(model, variables, var_exprs, 0, partial_g)

    def is_unary_predicate(self):
        return isinstance(self.get_exp(), nltk.sem.logic.ApplicationExpression) and (len(self.get_exp().free()) + len(self.get_exp().constants())) == 1

    def get_predicates(self):
        return [str(pred) for pred in self.get_exp().predicates()]

    def clone(self, var_map=dict(), symmetric=False):
        new_exp = self.get_exp()
        new_g = []
        new_variables = []
        for v in self._variables:
            if v in var_map:
                v_new = var_map[v]
                v_exp = nltk.sem.Expression.fromstring(v)
                v_new_exp = nltk.sem.Expression.fromstring(v_new)
                new_exp = new_exp.replace(v_exp.variable, v_new_exp, False)
                if v in self._init_g:
                    new_g.append((v_new, self._init_g[v]))
                new_variables.append(v_new)
            elif v in self._init_g:
                new_g.append((v, self._init_g[v]))
                new_variables.append(v)
            else:
                new_variables.append(v)

        new_form = OpenFormula(self._domain, str(new_exp), new_variables, nltk.Assignment(self._init_g.domain, new_g))
        if not symmetric:
            return new_form
        else:
            svars = sorted(new_variables)
            
            smap = dict()
            remp_map = dict()
            for i in range(len(new_variables)):
                smap[new_variables[i]] = svars[i] + "_p"
                remp_map[svars[i] + "_p"] = svars[i]             

            return new_form.clone(var_map=smap).clone(var_map=remp_map)


