#!/usr/bin/env bash
# Roda todos os testes de todos os niveis
python -m unittest discover -s banking.test -p "level_*_tests.py" -v
