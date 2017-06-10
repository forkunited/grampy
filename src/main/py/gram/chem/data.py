import operator

import gram.data as data
import gram.chem.rep as chem
import gram.fol.rep as fol
import gram.fol.data
from os import listdir
from os.path import isfile, join

class Datum(gram.fol.data.Datum):
    def __init__(self, molecule, value):
        self._molecule = molecule
        self._value = value
        self._label = value

    def get_value(self):
        return self._value
   
    def get_molecule(self):
        return self._molecule

    def get_model(self):
        return self._molecule.get_model()

    @staticmethod 
    def get_coulomb_matrix_fn(dimension):
        fn = lambda d : d.get_molecule().calculate_multilayer_coulomb_matrix(dimension=dimension)
        fn.__name__ = "Coulomb" # FIXME Hack
        return fn

class DataSet(gram.fol.data.DataSet):
    def __init__(self):
        data.DataSet.__init__(self)
        self._molecule_domain = ["0"]
        self._bond_type_counts = dict()

    def get_molecule_domain(self):
        return self._molecule_domain

    def get_bond_type_counts(self):
        return self._bond_type_counts

    def get_bond_types(self):
        return self._bond_type_counts.keys()

    def get_top_bond_types(self, k):
        tuples = sorted(self._bond_type_counts.items(), key=operator.itemgetter(1))
        tuples.reverse()
        return [tuples[i][0] for i in range(min(k, len(tuples)))]

    @staticmethod
    def make_from_xyz_dir(dir_path, value_property, max_size=None, includeHs=False):
        xyz_file_names = sorted(listdir(dir_path))
        xyz_files = []
        i = 0
        for f in xyz_file_names:
            f_path = join(dir_path, f)
            if not isfile(f_path):
                continue
            if i >= max_size:
                break
            xyz_files.append(f_path)
            i += 1
        
        D = DataSet()
        i = 0
        for xyz_file in xyz_files:
            if max_size is not None and i == max_size:
                break
            m = chem.Molecule.from_xyz_file(xyz_file, D._bond_type_counts, includeHs)
            if m is None:
                continue

            if m.get_n_a() > len(D._molecule_domain):
                D._molecule_domain = [str(i) for i in range(m.get_n_a())]

            value = m.get_property(value_property)
            D._data.append(Datum(m, value))
            i += 1
        return D


#class FeatureToken(data.FeatureToken):
#    def __init__(self, closed_form):
#        data.FeatureToken.__init__(self)
#        self._closed_form = closed_form
#
#    def get_closed_form(self):
#        return self._closed_form
#
#    def __str__(self):
#        return str(self._closed_form)
#
#
#class FeatureType(data.FeatureType):
#    def __init__(self, open_form):
#        data.FeatureType.__init__(self)
#        self._open_form = open_form
#
#    def get_open_form(self):
#        return self._open_form
#
#    def compute(self, datum):
#        closed_forms = self._open_form.get_closed_forms()
#        expr = self._open_form.get_form()
#        return [1.0 if datum.get_model().evaluate(expr, c.get_g()) else 0.0 for c in closed_forms]
#
#    def get_size(self):
#        return len(self._open_form.get_closed_forms())
#
#    def get_token(self, index):
#        return FeatureToken(self._open_form.get_closed_forms()[index])
#
#    def equals(self, feature_type):
#        my_g = self._open_form.get_init_g()
#        g = feature_type.get_open_form().get_init_g()
#
#        for v in my_g:
#            if v not in g or g[v] != my_g[v]:
#                return False 
#
#        return self._open_form.exp_matches(feature_type.get_open_form())
#
#
#class UnaryRule(data.UnaryRule):
#    def __init__(self, lhs_closed_form, rhs_open_form_fn):
#        data.UnaryRule.__init__(self)
#        self._lhs_closed_form = lhs_closed_form
#        self._rhs_open_form_fn = rhs_open_form_fn
#    
#    def matches(self, feature_token):
#        if not isinstance(feature_token, FeatureToken):
#            return False
#
#        if self._lhs_closed_form is None:
#            return True
#
#        f_form = feature_token.get_closed_form()
#
#        if not self._lhs_closed_form.matches(f_form):
#            return False
#
#        return True 
#
#    def apply(self, feature_token):
#        if not self.matches(feature_token):
#            return None
#        open_forms = self._rhs_open_form_fn(feature_token.get_closed_form())
#        return [FeatureType(open_form) for open_form in open_forms]
#
#class BinaryRule(data.BinaryRule):
#    def __init__(self, lhs_closed_form1, lhs_closed_form2, rhs_open_form_fn, ordered=False):
#        data.BinaryRule.__init__(self)
#        self._lhs_closed_form1 = lhs_closed_form1
#        self._lhs_closed_form2 = lhs_closed_form2
#        self._rhs_open_form_fn = rhs_open_form_fn
#        self._ordered = ordered
#
#    def matches(self, feature_token1, feature_token2):
#        if not isinstance(feature_token1, FeatureToken) or not isinstance(feature_token2, FeatureToken):
#            return False 
#        if self._lhs_closed_form1 is None and self._lhs_closed_form2 is None:
#            return True
#
#
#        f_form1 = feature_token1.get_closed_form()
#        f_form2 = feature_token2.get_closed_form()
#        if self._lhs_closed_form1.matches(f_form1) and self._lhs_closed_form2.matches(f_form2):
#            return True
#        if not self._ordered and self._lhs_closed_form1.matches(f_form2) and self._lhs_closed_form2.matches(f_form1):
#            return True
#        return False
#
#    def apply(self, feature_token1, feature_token2):
#        if not self.matches(feature_token1, feature_token2):
#            return None
#        open_forms = self._rhs_open_form_fn(feature_token1.get_closed_form(), feature_token2.get_closed_form())
#        return [FeatureType(open_form) for open_form in open_forms]

