import tensorflow as tf
from tensorflow.contrib import learn
import numpy as np
import feature

class NeuralModel:
    def __init__(self, F=None, hidden_1=400, hidden_2=100):
        self._F = F
        self._hidden_1 = hidden_1
        self._hidden_2 = hidden_2
        if F is not None:
            
            self._nn = self._make_nn(F, hidden_1=hidden_1, hidden_2=hidden_2)
        else:
            self._nn = None

        self._sess = None

    def _make_x(self, F):
        return tf.placeholder("float", [None, F.get_size()])

    def _make_y(self):
        return tf.placeholder("float", [None,1])

    def _make_nn(self, F, hidden_1, hidden_2=None):
        self._x = self._make_x(F)
        self._y = self._make_y()

        #out = tf.contrib.layers.flatten(self._x)
        out = tf.contrib.layers.fully_connected(inputs=self._x, num_outputs=hidden_1, weights_initializer = tf.contrib.layers.xavier_initializer(),
                 biases_initializer=tf.constant_initializer(0.0), activation_fn=tf.nn.relu)

        if hidden_2 is not None:
            out = tf.contrib.layers.fully_connected(inputs=out, num_outputs=hidden_2, weights_initializer = tf.contrib.layers.xavier_initializer(),
                 biases_initializer=tf.constant_initializer(0.0), activation_fn=tf.nn.relu)

        return tf.contrib.layers.fully_connected(inputs=out, num_outputs=1, weights_initializer = tf.contrib.layers.xavier_initializer(),
                 biases_initializer=tf.constant_initializer(0.0), activation_fn=None)

    def _mu(self, X):
        sess = self._sess
        if sess is None:
            sess = tf.Session()
        return sess.run(self._nn, { self._x : np.array([X]) })[0][0]

    def mu(self, datum):
        return self._mu(self._F.compute(datum))

    def predict(self, datum, rand=True):
        mu = self.mu(datum)
        if not rand:
            return mu
        else:
            return np.random.normal(mu, 1.0)

    def _make_train_data(self, D, F):
        M = feature.DataFeatureMatrix(D, F)
        X = np.asarray(M.get_matrix())
        Y = np.asarray([[D.get(i).get_label()] for i in range(D.get_size())])
        return X, Y

    def train(self, D, F, iterations=100, lr=0.001, batch_size=25, evaluation_fn=None):
        self._F = F

        # Defining placeholders as input
        self._nn = self._make_nn(F, hidden_1=self._hidden_1, hidden_2=self._hidden_2)

        # Define loss and optimizer
        cost = tf.reduce_mean(tf.square(self._nn-self._y))
        optimizer = tf.train.AdamOptimizer(learning_rate=lr).minimize(cost)

        X_train, Y_train = self._make_train_data(D, F)

        iters = []
        losses = []
        vals = []

        # Launch the graph
        with tf.Session() as sess:
            self._sess = sess
            sess.run(tf.global_variables_initializer())

            epochs = int(iterations/batch_size)
            index = 0
            # Training cycle
            for epoch in range(epochs):
                batch_x = X_train[index:(index+batch_size),:]
                batch_y = Y_train[index:(index+batch_size),:]
                # Run optimization op (backprop) and cost op (to get loss value)
                _, c, p = sess.run([optimizer, cost, self._nn], feed_dict={self._x: batch_x, self._y: batch_y})
                
                index += batch_size
                if index + batch_size > D.get_size():
                    index = 0
                    iteration = epoch*batch_size
                    loss = c

                    val = None
                    if evaluation_fn is not None:
                        val = evaluation_fn(self)
                        vals.append(val)

                    iters.append(iteration)
                    losses.append(loss)

                    iter_str = "Training nn model iteration " + str(iteration) + " loss: " + str(loss)
                    if val is not None:
                        iter_str += " eval: " + str(val)
                    print iter_str

        self._sess = None
        ret_history = dict()
        ret_history["iters"] = iters
        ret_history["losses"] = losses

        if len(vals) > 0:
            ret_history["vals"] = vals

        return ret_history

