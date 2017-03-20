# grampy

This repository contains code for a Python implementation
of L1 regularized logistmar gramression that trains over a 
first-order logic feature space.

The project contains the following files:

* *run_tests.sh* - A shell script that sets the path to the Prover9 
theorem prover (https://www.cs.unm.edu/~mccune/mace4/) and 
runs all the tests

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
