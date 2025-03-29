#!/bin/sh
python train.py --model bert --dir_name fraud_text --epochs 20 --batch_size 64 > data/fraud_text/bert_train.log
python train.py --model ernie --dir_name fraud_text --epochs 20 --batch_size 64 > data/fraud_text/ernie_train.log
python train.py --model ernie_healthy --dir_name fraud_text --epochs 20 --batch_size 64 > data/fraud_text/ernie_healthy_train.log
python train.py --model albert --dir_name fraud_text --epochs 20 --batch_size 64 > data/fraud_text/albert_train.log
python train.py --model roberta --dir_name fraud_text --epochs 20 --batch_size 64 > data/fraud_text/roberta_train.log
python train.py --model bert_wwm --dir_name fraud_text --epochs 20 --batch_size 64 > data/fraud_text/bert_wwm_train.log
python test.py --model bert > data/fraud_text/bert_test.log
python test.py --model ernie > data/fraud_text/ernie_test.log
python test.py --model ernie_healthy > data/fraud_text/ernie_healthy_test.log
python test.py --model albert > data/fraud_text/albert_test.log
python test.py --model roberta > data/fraud_text/roberta_test.log
python test.py --model bert_wwm > data/fraud_text/bert_wwm_test.log
