import unittest
import numpy as np
import nltk
import sys

import gram.model_linear as model_linear
import gram.model_nn as model_nn
import gram.model_mean as model_mean
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
from gram.chem.feature_atomic_bond import FeatureAtomType

FEATURES_0 = "FEATURES_0"
FEATURES_ATOM = "FEATURES_ATOM"
FEATURES_COULOMB = "FEATURES_COULOMB"

MODEL_L1 = "MODEL_L1"
MODEL_L1_G = "MODEL_L1_G"
MODEL_NN = "MODEL_NN"
MODEL_MEAN = "MODEL_MEAN"

DATA_DIR = sys.argv[1]
MODEL = sys.argv[2]
FEATURES = sys.argv[3]
DATA_SIZE = int(sys.argv[4]) # 400
PREDICTION_PROPERTY = sys.argv[5] # H, E_atomization
ITERATIONS = int(sys.argv[6]) # 4000
C_L1 = float(sys.argv[7]) # 0.01
GRAM_T = float(sys.argv[8]) # 10
ETA_0 = float(sys.argv[9]) # 0.01
LR = float(sys.argv[10]) # 0.01
BATCH_SIZE = float(sys.argv[11]) # 25
LAYERS = int(sys.argv[12]) # 1
HIDDEN_1 = None
HIDDEN_2 = None
if sys.argv[13] != "None":
    HIDDEN_1 = int(sys.argv[13])
if sys.argv[14] != "None":
    HIDDEN_2 = int(sys.argv[14])

print "Running with... "
print "Data: " + DATA_DIR
print "Model: " + MODEL
print "Features: " + FEATURES
print "Data size: " + str(DATA_SIZE)
print "Property: " + PREDICTION_PROPERTY
print "Iterations: " + str(ITERATIONS)
print "L1 reg: " + str(C_L1)
print "Gram t: " + str(GRAM_T)
print "Eta_0: " + str(ETA_0)
print "Lr: " + str(LR)
print "Batch size: " + str(BATCH_SIZE)
print "Layers: " + str(LAYERS)
print "Hidden 1: " + str(HIDDEN_1)
print "Hidden 2: " + str(HIDDEN_2) 
print "\n"

argv_len = len(sys.argv)
for i in range(1,argv_len):
    del sys.argv[argv_len-i] # Necessary to allow unittest.main() to work

np.random.seed(1)

class TestChemModel(unittest.TestCase):

    def _print_table(self, hist, name):
        print "iters, " + name
        for i in range(len(hist["iters"])):
            print "(" + str(hist["iters"][i]) + ", " + str(hist[name][i]) + ")"
        print "\n"

    def _print_tables(self, hist):
        for name in hist:
            if name == "iters":
                continue
            self._print_table(hist, name)

    def _load_data(self, prop, data_size):
        print "Loading data (" + str(data_size) + ")..."

        D = cdata.DataSet.make_from_xyz_dir(DATA_DIR, prop, max_size=data_size, includeHs=False) # E_atomization
        D_parts = D.split([0.5, 0.25, 0.25])
        D_train = D_parts[0]
        D_dev = D_parts[1]
        D_test = D_parts[2]

        print "Loaded bond types:"
        print str(D.get_bond_type_counts())

        return D, D_train, D_dev, D_test

    def _make_features_and_rules(self, features, D, bias):
        print "Making features and rules..."

        atomic_domain = D.get_molecule_domain()
        bond_types = D.get_top_bond_types(4) #["BOND"] #D.get_top_bond_types(4)

        F = feat.FeatureSet()
        if bias:
            F.add_feature_type(FeatureTopType())

        if features == FEATURES_ATOM:
            F.add_feature_type(FeatureAtomType(atomic_domain, includeHs=False))
        elif features == FEATURES_0:
            # NOTE: These were left out for isomers
            F.add_feature_type(FeatureAtomType(atomic_domain, includeHs=False))
            F.add_feature_type(FeatureAtomicBondType(atomic_domain, bond_types, includeHs=False))
        elif features == FEATURES_COULOMB:
            F.add_feature_type(feat.FeatureMatrixType("C", cdata.Datum.get_coulomb_matrix_fn(len(atomic_domain)), 3*len(atomic_domain)**2))

        R = rule.RuleSet()
        R.add_binary_rule(BinaryJoinPropertyRule())

        return F, R

    def _train_model(self, model_type, feature_type, D, F, R, eval_fn, params):
        out_str = "Training model (" + model_type + ", " + feature_type + ", data: " + str(D.get_size()) + ", "
        for param in params:
            out_str += param + ": " + str(params[param]) + ", "
        out_str = out_str[:(len(out_str)-2)] + ")"
        print out_str

        if model_type == MODEL_L1:
            m = model_linear.PredictionModel.make(model_linear.ModelType.LINEAR)
            hist = m.train_l1(D, F, iterations=params["iterations"], C=params["c_l1"], eta_0=params["eta_0"], alpha=0.8, evaluation_fn=eval_fn)
            return m, hist
        elif model_type == MODEL_L1_G:
            m = model_linear.PredictionModel.make(model_linear.ModelType.LINEAR)
            hist = m.train_l1_g(D, F, R, t=params["gram_t"], iterations=params["iterations"], C=params["c_l1"], eta_0=params["eta_0"], alpha=0.8, evaluation_fn=eval_fn)
            return m, hist
        elif model_type == MODEL_NN:
            hidden_1 = None
            hidden_2 = None
            if params["layers"] >= 1:
                if "hidden_1" in params:
                    hidden_1 = params["hidden_1"]
                else:
                    hidden_1 = F.get_size()     
            if params["layers"] == 2:
                if "hidden_2" in params:
                    hidden_2 = params["hidden_2"]
                else:
                    hidden_2 = F.get_size()
            m = model_nn.NeuralModel(F=F, hidden_1=hidden_1, hidden_2=hidden_2)#F_0.get_size(), hidden_2=F_0.get_size())
            hist = m.train(D, F, iterations=params["iterations"], lr=params["lr"], batch_size=params["batch_size"], evaluation_fn=eval_fn)
            return m, hist
        elif model_type == MODEL_MEAN:
            m = model_mean.MeanModel()
            hist = m.estimate(D,evaluation_fn=eval_fn)
            return m, hist
        else:
            return None

    def _test_model(self, model_type, data_size, features, prediction_property, params):
        D, D_train, D_dev, D_test = self._load_data(prediction_property, data_size)
        F, R = self._make_features_and_rules(features, D, True)
        eval_dev = evaluation.RMSE().for_data(D_dev)

        m, hist = self._train_model(model_type, features, D_train, F, R, eval_dev, params)

        if model_type != MODEL_NN:
            print "model"
            print str(m)

        print "histories"
        self._print_tables(hist)

    def test_linear(self):
        params = dict()
        params["iterations"] = ITERATIONS
        params["c_l1"] = C_L1
        params["gram_t"] = GRAM_T
        params["eta_0"] = ETA_0
        params["lr"] = LR
        params["batch_size"] = BATCH_SIZE
        params["layers"] = LAYERS
        if HIDDEN_1 is not None:
            params["hidden_1"] = HIDDEN_1
        if HIDDEN_2 is not None:
            params["hidden_2"] = HIDDEN_2
        self._test_model(MODEL, DATA_SIZE, FEATURES, PREDICTION_PROPERTY, params)

if __name__ == '__main__':
    unittest.main()

