#!/bin/bash

DATA_PATH=<PATH_TO DATA DIRECTORY>
TEST_DIR=src/test/py/gram/chem
PWD=`pwd`
export PYTHONPATH=$PYTHONPATH:${PWD}/src/main/py/
export PROVER9=<PATH TO PROVER9 BINARY>

if [ -z "$DATA_SIZE" ]; then
    export MODEL = "MODEL_L1"
    export FEATURES = "FEATURES_0"
    export DATA_SIZE="400"
    export PREDICTION_PROPERTY="H"
    export ITERATIONS="4000"
    export C_L1="0.01"
    export GRAM_T="10"
    export ETA_0="0.01"
    export LR="0.01"
    export BATCH_SIZE="25"
    export LAYERS="2"
    export HIDDEN_1="None"
    export HIDDEN_2="None"
fi

python ${TEST_DIR}/test_chem_data.py $DATA_PATH
python ${TEST_DIR}/test_chem_rules.py $DATA_PATH
python ${TEST_DIR}/test_chem_model.py $DATA_PATH ${DATA_PATH} ${MODEL} ${FEATURES} ${DATA_SIZE} ${PREDICTION_PROPERTY} ${ITERATIONS} ${C_L1} ${GRAM_T} ${ETA_0} ${LR} ${BATCH_SIZE} ${LAYERS} ${HIDDEN_1} ${HIDDEN_2}

