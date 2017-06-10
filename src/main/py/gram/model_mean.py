import numpy as np
import random
import data

class MeanModel(object):
    def __init__(self):
        self._mu = 0.0

    def __str__(self):
        return "mu\t" + str(self._mu) + "\n"

    def estimate(self, D, evaluation_fn=None):
        for i in range(D.get_size()):
            self._mu += D.get(i).get_label()
        self._mu /= D.get_size()
        
        ret_history = dict()
        ret_history["iters"] = [0]
        if evaluation_fn is not None:
            ret_history["vals"] = [evaluation_fn(self)]

        return ret_history

    def predict(self, datum, rand=True):
        if not rand:
            return self._mu
        else:
            return np.random.normal(self._mu, 1.0)

