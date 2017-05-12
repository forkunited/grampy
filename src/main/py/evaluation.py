import numpy as np
import abc

class Evaluation(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass

    def for_data(self, data):
        return lambda model: self.compute(model, data)

    @abc.abstractmethod
    def compute(self, model, data):
        """ Compute evaluation """


class RMSE(Evaluation):
    def __init__(self):
        pass

    def compute(self, model, data):
        rmse = 0.0
        for i in range(data.get_size()):
            datum = data.get(i)
            l = datum.get_label()
            l_hat = model.predict(datum)
            rmse += (l-l_hat)*(l-l_hat)
        return np.sqrt(rmse/data.get_size())


class Accuracy(Evaluation):
    def __init__(self):
        pass

    def compute(self, model, data):
        correct = 0.0
        for i in range(data.get_size()):
            datum = data.get(i)
            l = datum.get_label()
            l_hat = model.predict(datum)
            if l == l_hat:
                correct += 1
        return correct/data.get_size()
