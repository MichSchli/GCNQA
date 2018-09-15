#!/bin/bash

DATASET=$1

pipenv run python relation_prediction.py --input_file output.txt > predictions.txt
pipenv run python code/evaluate.py --predictions predictions.txt --gold $DATASET/train/gold_labels.txt
