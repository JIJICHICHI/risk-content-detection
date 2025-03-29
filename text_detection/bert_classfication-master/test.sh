#!/bin/sh
export TF_ENABLE_ONEDNN_OPTS=0
python test.py --model bert > data/fraud_text/bert_test.log
python test.py --model ernie > data/fraud_text/ernie_test.log
python test.py --model ernie_healthy > data/fraud_text/ernie_healthy_test.log
python test.py --model albert > data/fraud_text/albert_test.log
python test.py --model roberta > data/fraud_text/roberta_test.log
python test.py --model bert_wwm > data/fraud_text/bert_wwm_test.log
