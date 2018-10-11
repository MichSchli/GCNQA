#!/bin/bash

SCORE_FILE=$1

pipenv run python annotate_errors.py --question_file data/webquestions_small_valid/test_clean/sentences.conll --score_file $SCORE_FILE --relation_file data/webquestions_small_valid/test_clean/all_relations.min_1.txt --annotation_file error_annotation.txt --relation_count_file data/webquestions_small_valid/train/gold_relation_count.txt --gold_file data/webquestions_small_valid/test_clean/gold_labels.txt
