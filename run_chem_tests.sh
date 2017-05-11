#!/bin/bash

DATA_PATH=<PATH_TO DATA DIRECTORY>
TEST_DIR=src/test/py/chem
PWD=`pwd`
export PYTHONPATH=$PYTHONPATH:${PWD}/src/main/py/
export PROVER9=<PATH TO PROVER9 BINARY>

python ${TEST_DIR}/test_chem_data.py $DATA_PATH

