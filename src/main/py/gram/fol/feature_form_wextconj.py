""" Weighted extistential conjunction features """

from gram import feature
import copy

def _form_cmp(x,y):
    if x.is_unary_predicate() and not y.is_unary_predicate():
        return -1
    elif not x.is_unary_predicate() and y.is_unary_predicate():
        return 1
    else:
        return (y.get_form() > x.get_form()) - (y.get_form() < x.get_form())

class FeatureFormWextconjToken(feature.FeatureToken):
    def __init__(self, conjuncts, weight_fn, symmetric_rels=True):
        feature.FeatureToken.__init__(self)
        
        cs = list(conjuncts)        

        # FIXME Want this to sort by forms with variables removed (so that order is independent of 
        # variables.  This currently doesn't work correctly, but will cover the cases for which
        # it's currently used
        #
        # This also currently works untder the assumption that variables will appear in at least
        # one unary predicate
        cs.sort(cmp=_form_cmp)
        vmap = dict()
        var_index = 0
        for c in cs:
            vars_c = c.get_variables()        
            for var in vars_c:
                if var in vmap:
                    continue
                vmap[var] = "x" + str(var_index)
                var_index += 1

        for i in range(len(cs)):
            cs[i] = cs[i].clone(var_map=vmap, symmetric=symmetric_rels)

        cs.sort(cmp=_form_cmp) # Sort a second time to take new variable names into account

        self._conjuncts = cs

        self._open_conj = self._make_open_conj(cs)
        self._weight_fn = weight_fn

    def _make_open_conj(self, conjuncts):
        open_conj = conjuncts[0]
        for i in range(1, len(conjuncts)):
            open_conj = open_conj.conjoin(conjuncts[i])
        return open_conj

    def get_open_conj(self):
        return self._open_conj

    def get_weight_fn(self):
        return self._weight_fn

    def get_conjunct_count(self):
        return len(self._conjuncts)

    def get_conjunct(self, i):
        return self._conjuncts[i]

    def __str__(self):
        return str(self._open_conj.get_form()) + "_" + self._weight_fn.__name__ # FIXME Hack

    def compute(self, datum):
        sats = self._open_conj.satisfiers(datum.get_model()) 
        return self._weight_fn(datum, sats)

    def equals(self, feature_token):
        if not isinstance(feature_token, FeatureFormWextconjToken):
            return False

        if self._weight_fn.__name__ != feature_token._weight_fn.__name__:  # FIXME Hack
            return False

        for i in range(len(self._conjuncts)):
            if self._conjuncts[i].get_form() != feature_token._conjuncts[i].get_form():
                return False

        return True


class FeatureFormWextconjType(feature.FeatureType):
    def __init__(self, conjunct_lists, weight_fn, symmetric_rels=True):
        feature.FeatureType.__init__(self)

        self._symmetric_rels = symmetric_rels

        self._conjunct_lists = []
        for conjunct_list in conjunct_lists:
            clist = list(conjunct_list)
            clist.sort(cmp=lambda x, y : (y.get_form() > x.get_form()) - (y.get_form() < x.get_form()))
            self._conjunct_lists.append(clist)
        
        self._weight_fn = weight_fn
        self._tokens = self._make_feature_tokens()

    def _make_feature_tokens(self):
        tokens = self._make_feature_tokens_helper(0, [])
        unique_tokens = []
        for token in tokens:
            dup = False
            for unique_token in unique_tokens:
                if unique_token.equals(token):
                    dup = True
            if not dup:
                unique_tokens.append(token)
        return unique_tokens 


    def _make_feature_tokens_helper(self, conj_index, partial_conjs):
        if conj_index == len(self._conjunct_lists):
            return [FeatureFormWextconjToken(partial_conjs, self._weight_fn, symmetric_rels=self._symmetric_rels)]

        tokens = []
        for conj in self._conjunct_lists[conj_index]:
            next_conjs = copy.deepcopy(partial_conjs)
            next_conjs.append(conj)
            tokens.extend(self._make_feature_tokens_helper(conj_index + 1, next_conjs))
        return tokens

    def compute(self, datum):
        return [token.compute(datum) for token in self._tokens]

    def get_size(self):
        return len(self._tokens)

    def get_token(self, index):
        return self._tokens[index]

    def equals(self, feature_type):
        if not isinstance(feature_type, FeatureFormWextconjType):
            return False
        
        if self._weight_fn.__name__ != feature_type._weight_fn.__name__:  # FIXME Hack
            return False

        if len(self._conjunct_lists) != len(feature_type._conjunct_lists):
            return False

        for i in range(len(self._tokens)):
            if not self._tokens[i].equals(feature_type._tokens[i]):
                return False

        return True

