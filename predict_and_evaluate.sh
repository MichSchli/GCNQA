#!/bin/bash

REL_PRED_FILE=$1
DATASET=$2

pipenv run python relation_prediction_with_cached_entities.py --input_file $REL_PRED_FILE --entity_file data/entities.txt > predictions.txt
pipenv run python code/evaluate.py --predictions predictions.txt --gold $DATASET/gold_labels.txt
