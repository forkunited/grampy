import gram.fol.rep as fol
import gram.fol.feature_form_wextconj as fwextconj
import gram.chem.rep as chem

WEIGHT_SAT_COUNT = 0
WEIGHT_UNORDERED_SAT_COUNT = 1
WEIGHT_UNORDERED_UNIQ_SAT_COUNT = 2

def _unordered_uniq_sat_count(datum, sats):
    unordered_sats = set([])
    for sat in sats:
        if len(set(sat.values())) != len(sat.values()):
            continue
        unordered_sats.add(str(sorted(sat.values())))
    return len(unordered_sats)

def _unordered_sat_count(datum, sats):
    unordered_sats = set([])
    for sat in sats:
        unordered_sats.add(str(sorted(sat.values())))
    return len(unordered_sats)

class FeatureAtomicBondType(fwextconj.FeatureFormWextconjType):
    def __init__(self, molecule_domain, atomic_relations, weight_type=WEIGHT_UNORDERED_SAT_COUNT, includeHs=False):
        fwextconj.FeatureFormWextconjType.__init__(self, self._make_bond_conjuncts(molecule_domain, atomic_relations, includeHs), self._get_weight_fn(weight_type))

    def _make_bond_conjuncts(self, molecule_domain, atomic_relations, includeHs):
        props = chem.ATOMIC_PROPERTIES_NOH
        if includeHs:
            props = chem.ATOMIC_PROPERTIES

        atom_x_conjs = [fol.OpenFormula(molecule_domain, prop + "(x)", ["x"]) for prop in props]
        atom_y_conjs = [fol.OpenFormula(molecule_domain, prop  + "(y)", ["y"]) for prop in props]
        bond_xy_conjs = [fol.OpenFormula(molecule_domain, bond + "(x,y)", ["x","y"]) for bond in atomic_relations]

        return [atom_x_conjs, bond_xy_conjs, atom_y_conjs]

    def _get_weight_fn(self, weight_type):
        weight_fn = None
        if weight_type == WEIGHT_SAT_COUNT:
            weight_fn = lambda datum, sats: len(sats)
            weight_fn.__name__ = "SC"   # FIXME Hack
        elif weight_type == WEIGHT_UNORDERED_SAT_COUNT:
            weight_fn = _unordered_sat_count
            weight_fn.__name__ = "USC" # FIXME HACK
        elif weight_type == WEIGHT_UNORDERED_UNIQ_SAT_COUNT:
            weight_fn = _unordered_uniq_sat_count
            weight_fn.__name__ = "UUSC" # FIXME HACK

        return weight_fn

    def equals(self, feature_type):
        return isinstance(feature_type, FeatureAtomicBondType)

class FeatureAtomType(fwextconj.FeatureFormWextconjType):
    def __init__(self, molecule_domain, includeHs=False):
        fwextconj.FeatureFormWextconjType.__init__(self, self._make_atom_conjuncts(molecule_domain, includeHs), self._get_weight_fn())

    def _make_atom_conjuncts(self, molecule_domain, includeHs):
        props = chem.ATOMIC_PROPERTIES_NOH
        if includeHs:
            props = chem.ATOMIC_PROPERTIES

        atom_conjs = [fol.OpenFormula(molecule_domain, prop + "(x)", ["x"]) for prop in props]

        return [atom_conjs]

    def _get_weight_fn(self):
        weight_fn = lambda datum, sats: len(sats)
        weight_fn.__name__ = "SC"   # FIXME Hack
        return weight_fn

    def equals(self, feature_type):
        return isinstance(feature_type, FeatureAtomType)

