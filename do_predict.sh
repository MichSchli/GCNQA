#!/bin/bash

rm output_pred_temp.txt

pipenv run python code/analysis/extract_argmax.py --score_file output_backup.txt --relation_file data/webquestions_small_valid/test_clean/all_relations.min_1.entities.txt > output_pred_temp.txt

bash predict_and_evaluate.sh output_pred_temp.txt data/webquestions_small_valid/test_clean/
