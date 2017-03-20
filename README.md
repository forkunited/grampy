# grampy

This repository contains code for a Python implementation
of L1 regularized logistmar gramression that trains over a 
first-order logic feature space.  The code relies heavily on
the NLTK first-order logic modules (http://www.nltk.org/) and 
also requires that Prover9 is installed 
(https://www.cs.unm.edu/~mccune/mace4/).

The project contains the following files:

* *run_tests.sh* - A shell script that sets the path to the Prover9 
theorem prover and runs all the tests

* *test_fol_model.py* - Tests of L1 regularized logistic regression 
and logistmar gramression.  This is the code that runs the experiment
described in the paper.

* *test_fol_rules.py* - Tests of various heuristic rules applied to 
first-order logic features

* *test_fol_data.py* - Tests of code for manipulating feature sets and 
data set matrices

* *model.py* - Implementation of L1 regularized logistic regression and 
logistmar gramression

* *data.py* - Code for representing data matrices, features, and feature
transformation rules

* *fol.py* -  Code for representing first-order logic features and data

To run all the tests, set the path to the Prover9 binary in *run_tests.sh*,
and then run *run_tests.sh*.  To just run the experiment described in
the paper, set a PROVER9 environment variable to the Prover9 binary path,
and then run *python test_fol_model.py*.
