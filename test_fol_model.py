import unittest
import numpy as np
import nltk

import model
import fol
import data

class TestFOLModel(unittest.TestCase):

    def test_model(self):
        print "Starting test..."
        data_size = 3000
        properties_n = 5
        domain = ["0", "1", "2"]

        properties = []
        F_full = data.FeatureSet()
        F_relevant = data.FeatureSet()
        F_0 = data.FeatureSet()
        w = []
        R = data.RuleSet()

        feature = fol.FeatureTypeTop()
        F_full.add_feature_type(feature)
        F_relevant.add_feature_type(feature)
        F_0.add_feature_type(feature)
        w.append(-1.0)

        for i in range(properties_n):
            prop = "P" + str(i)
            properties.append(prop)

            form = fol.OpenFormula(domain, prop + "(x)", ["x"])
            feature = fol.FeatureType(form)
            F_full.add_feature_type(feature)            
            
            token_relevant = feature.get_token(0)
            form_relevant = fol.OpenFormula(domain, prop + "(x)", ["x"], init_g=token_relevant.get_closed_form().get_g())
            feature_relevant = fol.FeatureType(form_relevant)
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
                rP = fol.UnaryRule(cf, p_fn)
                R.add_unary_rule(rP)

            w.append(.1*2.0**i)
        
        model_true = model.LogLinearModel(F=F_relevant, w=np.array(w))
        label_fn = lambda d : model_true.classify(d)
        D = fol.DataSet.make_random(data_size, domain, properties, [], label_fn, seed=1)

        modell1 = model.LogLinearModel()
        modell1.train_l1(D, F_full, iterations=140001, C=16.0, eta_0=1.0, alpha=0.8)

        modell1_g = model.LogLinearModel()
        modell1_g.train_l1_g(D, F_0, R, t=0.04, iterations=140001, C=8.0, eta_0=1.0, alpha=0.8)


        print "True model"
        print str(model_true)

        print "l1 model"
        print str(modell1)

        print "l1-g model"
        print str(modell1_g)

        #self.assertEqual('foo'.upper(), 'FOO')

if __name__ == '__main__':
    unittest.main()
