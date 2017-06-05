import numpy as np
import random
import gram.fol.rep as fol
import data
import feature
import abc
from gram.fol.feature_top import FeatureTopToken


class ModelType:
    LINEAR = 0
    LOG_LINEAR = 1


class PredictionModel(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, w=None, F=None):
        self._w = w
        self._F = F

    @abc.abstractmethod
    def _gradient_i(self, M, i, w):
        """ Computes gradient on example i in M at w """

    @abc.abstractmethod
    def _loss_i(self, M, i, w):
        """ Computes loss on example M at w """

    @abc.abstractmethod
    def predict(self, datum, rand=True):
        """ Makes a prediction for a given datum """

    def __str__(self):
        s = ""
        for i in range(self._F.get_size()):
            s += str(self._F.get_feature_token(i)) + "\t" + str(self._w[i]) + "\n"
        return s


    def _eta(self, k, eta_0, alpha, N):
        return eta_0*(alpha**(k/(1.0*N)))


    def _apply_penalty_l1(self, i, w, u, q):
        z = w[i]
        if w[i] > 0:
            w[i] = max(0, w[i] - (u + q[i]))
        elif w[i] < 0:
            w[i] = min(0, w[i] + (u - q[i]))
        q[i] = q[i] + (w[i] - z)


    def _update_weights_l1(self, M, j, eta, w, u, q):
        g = self._gradient_i(M, j, w)
        for i in range(len(M.get_matrix()[0])):
            w[i] = w[i] + eta*g[i]
            if not isinstance(M.get_feature_set().get_feature_token(i), FeatureTopToken):
                self._apply_penalty_l1(i, w, u, q)


    def _extend_model_g(self, M, R, t, w, q):
        F = M.get_feature_set()

        expand_f = []
        for i in range(len(w)):
            if abs(w[i]) > t:
                expand_f.append(F.get_feature_token(i))
        
        new_f = R.apply(expand_f)
        M.extend(new_f)

        new_w = np.zeros(F.get_size() - len(w))
        new_q = np.zeros(F.get_size() - len(q))

        w = np.concatenate((w, new_w))
        q = np.concatenate((q, new_q))

        return w, q


    def _loss_l1(self, M, w, C):
        loss = 0.0
        for i in range(M.get_data().get_size()):
            loss += self._loss_i(M, i, w)

        l1 = 0.0
        nz = 0
        for i in range(len(w)):
            if not isinstance(M.get_feature_set().get_feature_token(i), FeatureTopToken):
                if abs(w[i]) > 0:
                    nz += 1
                l1 += abs(w[i])
                loss += C*abs(w[i])

        return loss, l1, nz


    # See http://aclweb.org/anthology/P/P09/P09-1054.pdf
    def train_l1(self, D, F, iterations=100, C=0.001, eta_0=1.0, alpha=0.8, evaluation_fn=None):
        D = D.copy()
        F = F.copy()
        M = feature.DataFeatureMatrix(D, F)
        u = 0
        w = np.zeros(F.get_size())
        q = np.zeros(F.get_size())
        N = D.get_size()
        iters = []
        losses = []
        l1s = []
        nzs = []
        vals = []
        for k in range(iterations):
            eta = self._eta(k, eta_0, alpha, N)
            if k % N == 0:
                M.shuffle()
                
                self._w = w
                self._F = F

                loss, l1, nz = self._loss_l1(M,w,C)
                val = None
                if evaluation_fn is not None:
                    val = evaluation_fn(self)
                    vals.append(val)

                iters.append(k)
                losses.append(loss)
                l1s.append(l1)
                nzs.append(nz)

                iter_str = "Training l1 model iteration " + str(k) + " eta: " + str(eta) + " loss: " + str(loss) + " l1: " + str(l1) + " nz: " + str(nz)
                if val is not None:
                    iter_str += " eval: " + str(val)
                print iter_str

            u += eta*C/N
            j = k % N
            self._update_weights_l1(M, j, eta, w, u, q)

        self._w = w
        self._F = F

        ret_history = dict()
        ret_history["iters"] = iters
        ret_history["losses"] = losses
        ret_history["l1s"] = l1s
        ret_history["nzs"] = nzs

        if len(vals) > 0:
            ret_history["vals"] = vals

        return ret_history


    def train_l1_g(self, D, F, R, t=0.0, iterations=100, C=0.001, eta_0=1.0, alpha=0.8, evaluation_fn=None):
        D = D.copy()
        F = F.copy()
        M = feature.DataFeatureMatrix(D, F)
        u = 0
        w = np.zeros(F.get_size())
        q = np.zeros(F.get_size())
        N = D.get_size()

        iters = []
        losses = []
        l1s = []
        nzs = []
        vals = []

        for k in range(iterations):
            eta = self._eta(k, eta_0, alpha, N)
            if k % N == 0:
                M.shuffle()

                self._w = w
                self._F = F

                loss, l1, nz = self._loss_l1(M,w,C)
                val = None
                if evaluation_fn is not None:
                    val = evaluation_fn(self)
                    vals.append(val)

                iters.append(k)
                losses.append(loss)
                l1s.append(l1)
                nzs.append(nz)

                w, q = self._extend_model_g(M, R, t, w, q)
                iter_str = "Training l1-g model iteration " + str(k) + " eta: " + str(eta) + " loss: " + str(loss) + " l1: " + str(l1) + " nz: " + str(nz)
                if val is not None:
                    iter_str += " eval: " + str(val)

                print iter_str

            u += eta*C/N

            j = k % N
            self._update_weights_l1(M, j, eta, w, u, q)

        self._w = w
        self._F = F

        ret_history = dict()
        ret_history["iters"] = iters
        ret_history["losses"] = losses
        ret_history["l1s"] = l1s
        ret_history["nzs"] = nzs

        if len(vals) > 0:
            ret_history["vals"] = vals

        return ret_history

    @staticmethod
    def make(model_type, w=None, F=None):
        if model_type == ModelType.LINEAR:
            return LinearModel(w, F)
        else:
            return LogLinearModel(w, F)


class LogLinearModel(PredictionModel):
    def __init__(self, w=None, F=None):
        PredictionModel.__init__(self, w, F)

    def _p(self, w, X):
        f = np.dot(w, X)
        return np.exp(f)/(1.0+np.exp(f))

    def p(self, datum):
        return self._p(self._w, self._F.compute(datum))

    def _gradient_i(self, M, i, w):
        l = M.get_data().get(i).get_label()
        X = M.get_matrix()[i]
        return X*(l-self._p(w,X))

    def _loss_i(self, M, i, w):
        l = M.get_data().get(i).get_label()
        X = M.get_matrix()[i]
        p = self._p(w,X)
        return -l*np.log(p)-(1.0-l)*(np.log(1.0-p))

    def predict(self, datum, rand=True):
        p = self.p(datum)
        if not rand:
            if p > 0.5:
                return 1.0
            else:
                return 0.0
        else:
            r = random.random()
            if r < p:
                return 1.0
            else:
                return 0.0


class LinearModel(PredictionModel):
    def __init__(self, w=None, F=None):
        PredictionModel.__init__(self, w, F)

    def _mu(self, w, X):
        return np.dot(w, X)

    def mu(self, datum):
        return self._mu(self._w, self._F.compute(datum))

    def _gradient_i(self, M, i, w):
        l = M.get_data().get(i).get_label()
        X = M.get_matrix()[i]

        return X*(l-self._mu(w,X))

    def _loss_i(self, M, i, w):
        l = M.get_data().get(i).get_label()
        X = M.get_matrix()[i]
        error = self._mu(w,X)-l
        return 0.5 * (error**2)

    def predict(self, datum, rand=True):
        mu = self.mu(datum)
        if not rand:
            return mu
        else:
            return np.random.normal(mu, 1.0)
