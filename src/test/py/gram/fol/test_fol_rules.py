import unittest
import data
import fol.rep as fol
import nltk

class TestFOLRules(unittest.TestCase):

    def test_rules(self):
        domain = ["0", "1", "2"]
        properties = ["P0", "P1", "P2", "P3"]
        binary_rels = ["R0", "R1", "R2", "R3"]

        F = data.FeatureSet()

        form0 = fol.OpenFormula(domain, "P0(x)", ["x"])
        feature0 = fol.FeatureType(form0)
        F.add_feature_type(feature0)        

        form1 = fol.OpenFormula(domain, "P1(x)", ["x"])
        feature1 = fol.FeatureType(form1)
        F.add_feature_type(feature1)

        form2 = fol.OpenFormula(domain, "P2(x)", ["x"])
        feature2 = fol.FeatureType(form2)
        #F.add_feature_type(feature2)

        rs = data.RuleSet()

        # Binary rule conjunction
        def conj_fn(cf1, cf2): 
            cf2_o = cf2.orthogonize(cf1)
            new_g = cf2_o.get_g().copy()
            new_g.update(cf1.get_g())
            return [fol.OpenFormula(domain, str(cf1.get_exp() & cf2_o.get_exp()), new_g.keys(), init_g=new_g)]
        rConj = fol.BinaryRule(None, None, conj_fn)
        rs.add_binary_rule(rConj)

        # Test conjunction
        F_tokens = [F.get_feature_token(i) for i in range(F.get_size())]
        for i in range(len(F_tokens)):
            self.assertTrue(F_tokens[i] is not None)
        
        output_forms = rs.apply(F_tokens)
        self.assertEquals(len(output_forms), len(F_tokens)*(len(F_tokens)-1))

        # Binary rule specific disjunction
        def disj_fn(cf1, cf2): 
            cf2_o = cf2.orthogonize(cf1)
            new_g = cf2_o.get_g().copy()
            new_g.update(cf1.get_g())
            return [fol.OpenFormula(domain, str(cf1.get_exp() | cf2_o.get_exp()), new_g.keys(), init_g=new_g)]
        cf0 = fol.ClosedFormula(form0.get_form(), nltk.Assignment(domain, []))
        rDisj0 = fol.BinaryRule(cf0, cf0, disj_fn)
        rs.add_binary_rule(rDisj0)

        output_forms = rs.apply(F_tokens)
        self.assertEquals(len(output_forms), len(F_tokens)*(len(F_tokens)-1) + len(domain)*(len(domain)-1))

        # Unary rule introduce existential
        # Introducing exists through a string is probably the wrong way to do this
        def exist_fn(cf): 
            ofs = []
            for var in cf.get_g():
                new_g = cf.get_g().copy()
                del new_g[var]
                ofs.append(fol.OpenFormula(domain, "exists " + var + "." + cf.get_form(), new_g.keys(), init_g=new_g))
            return ofs
        rExistI = fol.UnaryRule(None, exist_fn)
        rs.add_unary_rule(rExistI)

        # FIXME Maybe do later: Unary rule remove existential

        # Unary rule 0 => 2
        def p_2_fn(cf):
            ofs = []
            for var in cf.get_g():
                ofs.append(fol.OpenFormula(domain, "P2(" + var + ")", [var], init_g=nltk.Assignment(domain,[(var, cf.get_g()[var])])))
            return ofs
        rP0_2 = fol.UnaryRule(cf0, p_2_fn)
        rs.add_unary_rule(rP0_2)

        output_forms = rs.apply(F_tokens)
        for i in range(len(output_forms)):
            self.assertTrue(output_forms[i] is not None)

        #print len(output_forms)
        #for i in range(len(output_forms)):
        #    print output_forms[i].get_token(0).get_closed_form().get_form() + "\t" + str(output_forms[i].get_token(0).get_closed_form().get_g())

          

if __name__ == '__main__':
    unittest.main()
