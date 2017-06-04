import numpy as np
from gram import data

class FeatureToken:
    def __init__(self):
        pass


class FeatureType:
    def __init__(self):
        pass


class FeatureSet:
    def __init__(self, feature_types=[]):
        self._feature_types = list(feature_types)
        self._size = sum([feature_type.get_size() for feature_type in feature_types])

    def has_feature_type(self, feature_type):
        for f in self._feature_types:
            if f.equals(feature_type):
                return True
        return False

    def add_feature_type(self, feature_type):
        if self.has_feature_type(feature_type):
            return False
        self._feature_types.append(feature_type)
        self._size += feature_type.get_size()
        return True

    def add_feature_types(self, feature_types):
        ret = True
        for feature_type in feature_types:
            r = self.add_feature_type(feature_type)
            ret = r and ret
        return ret

    def get_size(self):
        return self._size

    def get_num_feature_types(self):
        return len(self._feature_types)

    def compute(self, datum, start_from=0):
        v = []
        for i in range(start_from, len(self._feature_types)):
            v.extend(self._feature_types[i].compute(datum))
        return np.array(v)

    def get_feature_token(self, index):
        offset = 0
        for i in range(len(self._feature_types)):
            if index < offset + self._feature_types[i].get_size():
                return self._feature_types[i].get_token(index - offset)
            else:
                offset += self._feature_types[i].get_size()
        return None

    def get_feature_type(self, index):
        return self._feature_types[index]

    def copy(self):
        return FeatureSet(feature_types=self._feature_types)


class DataFeatureMatrix:
    def __init__(self, data, feature_set):
        self._data = data
        self._feature_set = feature_set
        self._compute()

    def get_data(self):
        return self._data

    def get_feature_set(self):
        return self._feature_set

    def get_matrix(self):
        return self._mat

    def extend(self, feature_types):
        start_num = self._feature_set.get_num_feature_types()
        self._feature_set.add_feature_types(feature_types)
        for i in range(self._data.get_size()):
            new_vec = self._feature_set.compute(self._data.get(i), start_from=start_num)
            self._mat[i] = np.concatenate((self._mat[i], new_vec))

    def _compute(self):
        self._mat = []
        for i in range(self._data.get_size()):
            self._mat.append(self._feature_set.compute(self._data.get(i)))

    def shuffle(self):
        perm = np.random.permutation(len(self._mat))
        shuffled_mat = []
        shuffled_data = []
        for i in range(len(perm)):
            shuffled_mat.append(self._mat[perm[i]])
            shuffled_data.append(self._data.get(perm[i]))
        self._data = data.DataSet(data=shuffled_data)
        self._mat = shuffled_mat


