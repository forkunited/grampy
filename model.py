import numpy as np
import random
import fol
import data

class LogLinearModel:
    def __init__(self, w=None, F=None):
        self._w = w
        self._F = F

    def __str__(self):
        s = ""
        for i in range(self._F.get_size()):
            s += str(self._F.get_feature_token(i)) + "\t" + str(self._w[i]) + "\n"
        return s

    def _p(self, w, X):
        f = np.dot(w, X)
        return np.exp(f)/(1.0+np.exp(f))


    def p(self, datum):
        return self._p(self._w, self._F.compute(datum))

    def classify(self, datum):
        p = self.p(datum)
        #if p > 0.5:
        #    return 1.0
        #else:
        #    return 0.0
        r = random.random()
        if r < p:
            return 1.0
        else:
            return 0.0

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
        l = M.get_data().get(j).get_label()
        X = M.get_matrix()[j]
        g = X*(l-self._p(w,X))
        #print str(X[len(X)-3]) + " " + str(l)
        for i in range(len(M.get_matrix()[0])): 
            w[i] = w[i] + eta*g[i]
            if not isinstance(M.get_feature_set().get_feature_token(i), fol.FeatureTokenTop):
                self._apply_penalty_l1(i, w, u, q)

    def _ll_l1(self, M, w, C):
        ll = 0.0
        for i in range(M.get_data().get_size()):
            l = M.get_data().get(i).get_label()
            X = M.get_matrix()[i]
            p = self._p(w,X)
            ll += l*np.log(p)+(1.0-l)*(np.log(1.0-p)) 
        
        l1 = 0.0
        nz = 0
        for i in range(len(w)):
            if not isinstance(M.get_feature_set().get_feature_token(i), fol.FeatureTokenTop):
                if abs(w[i]) > 0:
                    nz += 1
                l1 += abs(w[i])
                ll -= C*abs(w[i])

        return ll, l1, nz

    # See http://aclweb.org/anthology/P/P09/P09-1054.pdf
    def train_l1(self, D, F, iterations=100, C=0.001, eta_0=1.0, alpha=0.8):
        D = D.copy()
        F = F.copy()
        M = data.DataFeatureMatrix(D, F)
        u = 0
        w = np.zeros(F.get_size())
        q = np.zeros(F.get_size())
        N = D.get_size()
        iters = []
        lls = []
        l1s = []
        nzs = []
        for k in range(iterations):
            eta = self._eta(k, eta_0, alpha, N)
            if k % N == 0:
                M.shuffle()
                ll, l1, nz = self._ll_l1(M,w,C)
                
                iters.append(k)
                lls.append(ll)
                l1s.append(l1)
                nzs.append(nz)
                
                print "Training l1 model iteration " + str(k) + " eta: " + str(eta) + " ll: " + str(ll) + " l1: " + str(l1) + " nz: " + str(nz)

            u += eta*C/N
            j = k % N
            self._update_weights_l1(M, j, eta, w, u, q)

        self._w = w
        self._F = F

        ret_history = dict()
        ret_history["iters"] = iters
        ret_history["lls"] = lls
        ret_history["l1s"] = l1s
        ret_history["nzs"] = nzs        

        return ret_history


    def _extend_model_g(self, M, R, t, w, q):
        F = M.get_feature_set()

        expand_f = []
        for i in range(len(w)):
            if w[i] > t:
                expand_f.append(F.get_feature_token(i))

        new_f = R.apply(expand_f)
        M.extend(new_f)

        new_w = np.zeros(F.get_size() - len(w))
        new_q = np.zeros(F.get_size() - len(q))

        w = np.concatenate((w, new_w))
        q = np.concatenate((q, new_q))

        return w, q


    def train_l1_g(self, D, F, R, t=0.0, iterations=100, C=0.001, eta_0=1.0, alpha=0.8):
        D = D.copy()
        F = F.copy()
        M = data.DataFeatureMatrix(D, F)
        u = 0
        w = np.zeros(F.get_size())
        q = np.zeros(F.get_size())
        N = D.get_size()

        iters = []
        lls = []
        l1s = []
        nzs = []

        for k in range(iterations):
            eta = self._eta(k, eta_0, alpha, N)
            if k % N == 0:
                M.shuffle()
                ll, l1, nz = self._ll_l1(M,w,C)
                
                iters.append(k)
                lls.append(ll)
                l1s.append(l1)
                nzs.append(nz)

                w, q = self._extend_model_g(M, R, t, w, q)
                print "Training l1-g model iteration " + str(k) + " eta: " + str(eta) + " ll: " + str(ll) + " l1: " + str(l1) + " nz: " + str(nz)

            u += eta*C/N

            j = k % N
            self._update_weights_l1(M, j, eta, w, u, q)

        self._w = w
        self._F = F

        ret_history = dict()
        ret_history["iters"] = iters
        ret_history["lls"] = lls
        ret_history["l1s"] = l1s
        ret_history["nzs"] = nzs

        return ret_history

