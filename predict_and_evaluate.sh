#!/bin/bash

REL_PRED_FILE=$1
DATASET=$2

pipenv run python relation_prediction.py --input_file $REL_PRED_FILE > predictions.txt
pipenv run python code/evaluate.py --predictions predictions.txt --gold $DATASET/train/gold_labels.txt
