#!/bin/bash

GPU_ID=$1

CUDA_VISIBLE_DEVICES=$GPU_ID pipenv run python train.py