import unittest
import gram.rule as rule
import gram.data as data
import gram.feature as feat
import gram.fol.rep as fol
import gram.chem.feature_atomic_bond as fbond
import gram.chem.data as cdata
from gram.fol.rule_form_wextconj import BinaryJoinPropertyRule
import nltk
import sys

DATA_DIR = sys.argv[1]

del sys.argv[1] # Necessary to allow unittest.main() to work

class TestChemRules(unittest.TestCase):

    def test_rules(self):
        D = cdata.DataSet.make_from_xyz_dir(DATA_DIR, "H", max_size=1)
        atomic_domain = D.get_molecule_domain()

        f = fbond.FeatureAtomicBondType(atomic_domain)
        F = feat.FeatureSet()
        F.add_feature_type(f)

        fmat = feat.DataFeatureMatrix(D, F)

        print "Features"
        for i in range(F.get_size()):
            print str(F.get_feature_token(i))

        rs = rule.RuleSet()
        rs.add_binary_rule(BinaryJoinPropertyRule())
        F.add_feature_types(rs.apply([F.get_feature_token(i) for i in range(2)]))

        print "Output Features"
        for i in range(F.get_num_feature_types()):
            ftype = F.get_feature_type(i)
            for j in range(ftype.get_size()):
                print str(ftype.get_token(j))


if __name__ == '__main__':
    unittest.main()
