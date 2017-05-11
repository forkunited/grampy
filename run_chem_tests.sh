#!/bin/bash

DATA_PATH=<PATH_TO DATA DIRECTORY>
TEST_DIR=src/test/py/fol
PWD=`pwd`
export PYTHONPATH=$PYTHONPATH:${PWD}/src/main/py/
export PROVER9=<PATH TO PROVER BINARY>

python test_chem_data.py $DATA_PATH

