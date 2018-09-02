#!/bin/bash

cp ~/Projects/Mindblocks2.0/dist/Mindblocks-0.0.1-py3-none-any.whl lib/
pipenv --rm
pipenv install
