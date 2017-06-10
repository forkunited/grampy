import unittest
import gram.chem.data as cdata
import gram.data as data
import gram.feature as feature
import gram.chem.feature_atomic_bond as fbond
import sys
import time

DATA_DIR = sys.argv[1]

del sys.argv[1] # Necessary to allow unittest.main() to work

class TestChemData(unittest.TestCase):
    #def test_data_load(self):
    #    D = cdata.DataSet.make_from_xyz_dir(DATA_DIR, "H", max_size=10) # H is enthalpy
    #    for i in range(D.get_size()):
    #        datum = D.get(i)
    #        self.assertEqual(datum.get_molecule().get_property("H"), datum.get_value())

    def test_molecule_features(self):
        D = cdata.DataSet.make_from_xyz_dir(DATA_DIR, "H", max_size=1)
        atomic_domain = D.get_molecule_domain()
        atomic_domain_size = len(atomic_domain)

        f = fbond.FeatureAtomicBondType(atomic_domain, D.get_bond_types())
        F = feature.FeatureSet()
        F.add_feature_type(f)
        
        fmat = None
        mat = None
        f_start = time.time()
        for i in range(100):
            fmat = feature.DataFeatureMatrix(D, F)
            mat = fmat.get_matrix()
        print "Computing features 100 times took: " + str(time.time() - f_start)

        print "Molecule bonds"
        print D.get(0).get_molecule().get_structure_str() 

        print "Features"
        for i in range(f.get_size()):
            print str(f.get_token(i)) + ": " + str(mat[0][i])

        print "Coulomb matrix stuff..."
        f_c = feature.FeatureMatrixType("C", cdata.Datum.get_coulomb_matrix_fn(atomic_domain_size), 3*atomic_domain_size**2)
        F_c = feature.FeatureSet()
        F_c.add_feature_type(f_c)
        fmat_c = feature.DataFeatureMatrix(D, F_c)
        mat_c = fmat_c.get_matrix()
        for i in range(f_c.get_size()):
            print str(f_c.get_token(i)) + ": " + str(mat_c[0][i])


if __name__ == '__main__':
    unittest.main()
