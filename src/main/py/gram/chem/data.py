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

    def get_value(self):
        return self._value
   
    def get_molecule(self):
        return self._molecule

    def get_model(self):
        return self._molecule.get_model()

class DataSet(gram.fol.data.DataSet):
    def __init__(self):
        data.DataSet.__init__(self)

    @staticmethod
    def make_from_xyz_dir(dir_path, value_property):
        xyz_files = sorted([join(dir_path, f) for f in listdir(dir_path) if isfile(join(dir_path, f))])
        D = data.DataSet()
        for xyz_file in xyz_files:
            m = chem.Molecule.from_xyz_file(xyz_file)
            value = m.get_property(value_property)
            D._data.append(Datum(m, value))
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

