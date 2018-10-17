#!/bin/bash

LOGICGPU=$1
SERVER=logicgpu$LOGICGPU

rsync --update -avh . $SERVER:/home/mschlic1/GCNQA_mindblocks
