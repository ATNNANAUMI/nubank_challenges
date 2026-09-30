#!/usr/bin/env bash
# Roda um unico caso: bash run_single_test.sh "test_level_1_case_01_create_account"
python -m unittest discover -s cloud.test -p "*_tests.py" -k "$1" -v
