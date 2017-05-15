import unittest
import numpy as np
import nltk

import gram.model_linear as model_linear
import gram.fol.rep as fol
import gram.data as data
import gram.feature as feat
import gram.rule as rule
import gram.evaluation as evaluation
import gram.fol.data 

from gram.fol.rule_form_indicator import BinaryRule
from gram.fol.rule_form_indicator import UnaryRule
from gram.fol.feature_top import FeatureTopType
from gram.fol.feature_form_indicator import FeatureFormIndicatorType

np.random.seed(1)

class TestFOLModel(unittest.TestCase):

    def _print_table(self, hist, name):
        print "iters, " + name
        for i in range(len(hist["iters"])):
            print "(" + str(hist["iters"][i]) + ", " + str(hist[name][i]) + ")"
        print "\n"

    def _test_model(self, model_type, eta_0, evaluate):
        print "Starting test..."
        data_size = 3000
        properties_n = 5
        domain = ["0", "1", "2"]

        properties = []
        F_full = feat.FeatureSet()
        F_relevant = feat.FeatureSet()
        F_0 = feat.FeatureSet()
        w = []
        R = rule.RuleSet()

        feature = FeatureTopType()
        F_full.add_feature_type(feature)
        F_relevant.add_feature_type(feature)
        F_0.add_feature_type(feature)
        w.append(-1.0)

        for i in range(properties_n):
            prop = "P" + str(i)
            properties.append(prop)

            form = fol.OpenFormula(domain, prop + "(x)", ["x"])
            feature = FeatureFormIndicatorType(form)
            F_full.add_feature_type(feature)            
            
            token_relevant = feature.get_token(0)
            form_relevant = fol.OpenFormula(domain, prop + "(x)", ["x"], init_g=token_relevant.get_closed_form().get_g())
            feature_relevant = FeatureFormIndicatorType(form_relevant)
            F_relevant.add_feature_type(feature_relevant)

            if i == 0:
                F_0.add_feature_type(feature)
            else:
                def p_fn(cf, i=i):
                    ofs = []
                    for var in cf.get_g():
                        ofs.append(fol.OpenFormula(domain, "P" + str(i) + "(" + var + ")", [var], init_g=nltk.Assignment(domain,[(var, cf.get_g()[var])])))
                    return ofs
                cf = fol.ClosedFormula("P" + str(i-1) + "(x)", nltk.Assignment(domain, []))
                rP = UnaryRule(cf, p_fn)
                R.add_unary_rule(rP)

            w.append(.1*2.0**i)
        
        model_true = model_linear.PredictionModel.make(model_type, F=F_relevant, w=np.array(w))
        label_fn = lambda d : model_true.predict(d)
        D = gram.fol.data.DataSet.make_random(data_size, domain, properties, [], label_fn)

        D_parts = D.split([0.8, 0.1, 0.1])
        D_train = D_parts[0]
        D_dev = D_parts[1]
        
        eval_dev = evaluate.for_data(D_dev)        

        modell1 = model_linear.PredictionModel.make(model_type)
        l1_hist = modell1.train_l1(D, F_full, iterations=140001, C=16.0, eta_0=eta_0, alpha=0.8, evaluation_fn=eval_dev)

        modell1_g = model_linear.PredictionModel.make(model_type)
        l1_g_hist = modell1_g.train_l1_g(D, F_0, R, t=0.04, iterations=140001, C=8.0, eta_0=eta_0, alpha=0.8, evaluation_fn=eval_dev)

        print "True model"
        print str(model_true)

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
        print "Linear model..."
        self._test_model(model_linear.ModelType.LINEAR, 0.1, evaluation.RMSE())

    def test_log_linear(self):
        print "Log-linear model..."
        self._test_model(model_linear.ModelType.LOG_LINEAR, 1.0, evaluation.Accuracy())


if __name__ == '__main__':
    unittest.main()

