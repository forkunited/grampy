import numpy as np

class DataSet:
    def __init__(self):
        self._data = []

    def get(self, i):
        return self._data[i]

    def get_data(self):
        return self._data

    def get_size(self):
        return len(self._data)


class FeatureToken:
    def __init__(self):
        pass


class FeatureType:
    def __init__(self):
        pass


class FeatureSet:
    def __init__(self):
        self._feature_types = []
        self._size = 0

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


class UnaryRule:
    def __init__(self):
        pass


class BinaryRule:
    def __init__(self):
        pass


class RuleSet:
    def __init__(self):
        self._unary_rules = []
        self._binary_rules = []

    def add_unary_rule(self, rule):
        self._unary_rules.append(rule)

    def add_binary_rule(self, rule):
        self._binary_rules.append(rule)

    def _apply_unary_rules(self, feature_token, results):
        for rule in self._unary_rules:
            if rule.matches(feature_token):
                results.extend(rule.apply(feature_token))
        return results

    def _apply_binary_rules(self, feature_token1, feature_token2, results):
        for rule in self._binary_rules:
            if rule.matches(feature_token1, feature_token2):
                results.extend(rule.apply(feature_token1, feature_token2))
        return results

    def apply(self, feature_tokens):
        results = [] 
        for i in range(len(feature_tokens)):
            self._apply_unary_rules(feature_tokens[i], results)
            for j in range(0, len(feature_tokens)):
                if i != j:
                    self._apply_binary_rules(feature_tokens[i], feature_tokens[j], results)
        return results


