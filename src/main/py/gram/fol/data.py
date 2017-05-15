from gram import data
import rep


class Datum:
    def __init__(self, model):
        self._model = model

    def get_label(self):
        return self._label

    def get_model(self):
        return self._model

    @staticmethod
    def make_random(domain, properties, binary_rels, label_fn):
        m = rep.RelationalModel.make_random(domain, properties, binary_rels)
        d = Datum(m)
        d._label = label_fn(d)
        return d


class DataSet(data.DataSet):
    def __init__(self):
        data.DataSet.__init__(self)

    @staticmethod
    def make_random(size, domain, properties, binary_rels, label_fn):
        D = DataSet()
        for i in range(0, size):
            D._data.append(Datum.make_random(domain, properties, binary_rels, label_fn))
        return D
