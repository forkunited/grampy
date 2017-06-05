import unittest
import numpy as np
import nltk
import sys

import gram.model_linear as model_linear
import gram.fol.rep as fol
import gram.data as data
import gram.feature as feat
import gram.rule as rule
import gram.evaluation as evaluation
import gram.chem.data as cdata 
import gram.chem.rep as chem

from gram.fol.rule_form_wextconj import BinaryJoinPropertyRule
from gram.fol.feature_top import FeatureTopType
from gram.chem.feature_atomic_bond import FeatureAtomicBondType

DATA_DIR = sys.argv[1]

del sys.argv[1] # Necessary to allow unittest.main() to work

np.random.seed(1)

class TestChemModel(unittest.TestCase):

    def _print_table(self, hist, name):
        print "iters, " + name
        for i in range(len(hist["iters"])):
            print "(" + str(hist["iters"][i]) + ", " + str(hist[name][i]) + ")"
        print "\n"

    def _test_model(self, model_type, eta_0, evaluate):
        data_size = 10

        print "Loading data (" + str(data_size) + ")..."

        D = cdata.DataSet.make_from_xyz_dir(DATA_DIR, "E_atomization", max_size=data_size)
        D_parts = D.split([0.8, 0.1, 0.1])
        D_train = D_parts[0]
        D_dev = D_parts[1]
        
        print "Loaded bond types:"
        print str(D.get_bond_type_counts())

        print "Making features and rules..."

        atomic_domain = D.get_molecule_domain()
        bond_types = D.get_top_bond_types(4)

        F_0 = feat.FeatureSet()
        F_0.add_feature_type(FeatureTopType())
        F_0.add_feature_type(FeatureAtomicBondType(atomic_domain, bond_types))

        R = rule.RuleSet()
        R.add_binary_rule(BinaryJoinPropertyRule())

        eval_dev = evaluate.for_data(D_dev)        

        print "Running l1 model..."

        modell1 = model_linear.PredictionModel.make(model_type)
        l1_hist = modell1.train_l1(D, F_0, iterations=1000, C=8.0, eta_0=eta_0, alpha=0.8, evaluation_fn=eval_dev)

        print "Running grammar model..." 

        modell1_g = model_linear.PredictionModel.make(model_type)
        l1_g_hist = modell1_g.train_l1_g(D, F_0, R, t=0.04, iterations=1000, C=8.0, eta_0=eta_0, alpha=0.8, evaluation_fn=eval_dev)

        print "l1 model"
        print str(modell1)

        print "l1-g model"
        print str(modell1_g)

        print "l1 histories"
        self._print_table(l1_hist, "losses")
        self._print_table(l1_hist, "l1s")
        self._print_table(l1_hist, "nzs")
        self._print_table(l1_hist, "vals")

        print "l1-g histories"
        self._print_table(l1_g_hist, "losses")
        self._print_table(l1_g_hist, "l1s")
        self._print_table(l1_g_hist, "nzs")
        self._print_table(l1_g_hist, "vals")


    def test_linear(self):
        print "Linear model test..."
        self._test_model(model_linear.ModelType.LINEAR, 0.01, evaluation.RMSE())

if __name__ == '__main__':
    unittest.main()

