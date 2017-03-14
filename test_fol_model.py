import unittest
import numpy as np

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
        w = []

        feature = fol.FeatureTypeTop()
        F_full.add_feature_type(feature)
        F_relevant.add_feature_type(feature)
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

            w.append(.1*2.0**i)
        
        model_true = model.LogLinearModel(F=F_relevant, w=np.array(w))
        label_fn = lambda d : model_true.classify(d)
        D = fol.DataSet.make_random(data_size, domain, properties, [], label_fn, seed=1)

        modell1 = model.LogLinearModel()
        modell1.train_l1(D, F_full, iterations=140001, C=16.0, eta_0=1.0, alpha=0.8)

        print "True model"
        print str(model_true)

        print "l1 model"
        print str(modell1)

        #self.assertEqual('foo'.upper(), 'FOO')

if __name__ == '__main__':
    unittest.main()
