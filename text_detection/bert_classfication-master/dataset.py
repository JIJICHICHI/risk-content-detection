# -*- coding: utf-8 -*-
from collections import Counter
import re
from matplotlib import pyplot as plt
from torch.utils.data import Dataset
import pandas as pd
import torch
from config import *


class DataPrecessForSentence(Dataset):
    """
    对文本进行处理
    """

    def __init__(self, bert_tokenizer, args, type='train'):
        """
        bert_tokenizer : 分词器
        LCQMC_file     : 语料文件
        """
        self.bert_tokenizer = bert_tokenizer
        self.type_ = type
        self.data = self.get_input(args)

    def __len__(self):
        return self.length

    def __getitem__(self, idx):
        return {k: v[idx] for k, v in self.data.items()}

    def plot_data_info(self, labels, args):
        import matplotlib.pyplot as plt
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        print('各个分类标签个数')
        label_count = Counter(labels)
        x = list(label_count.keys())
        y = list(label_count.values())
        plt.barh(x, y, height=0.7, left=0, color='c', edgecolor='r')
        plt.savefig(args.data_info_file)

    def get_input(self, args):
        """
        通过输入文本进行分词、ID化、截断、填充等流程得到最终的可用于模型输入的序列。
        """
        if self.type_ == 'train':
            file = args.train_file
        elif self.type_ == 'dev':
            file = args.dev_file
        else:
            file = args.test_file

        # 使用新的on_bad_lines参数替代error_bad_lines
        if self.type_ == 'train' and args.read_n_num:
            df = pd.read_csv(file, engine='python', encoding=args.csv_encoding,
                             nrows=args.read_n_num, sep=args.csv_sep, on_bad_lines='skip')
        else:
            df = pd.read_csv(file, engine='python', encoding=args.csv_encoding,
                             sep=args.csv_sep, on_bad_lines='skip')

        self.length = len(df)
        self.bert_tokenizer.model_max_length = args.max_seq_len
        print(f"数据集个数为{len(df)}")

        sentences = df[args.text_col_name].tolist()
        if args.class_col_name:
            labels = df[args.class_col_name].tolist()
        else:
            print('没有标签，全部设置为1')
            labels = [1 for _ in range(self.length)]

        # 使用分词器处理文本
        data = self.bert_tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')

        self.labels = labels.copy()
        if args.problem_type == 'multi_label_classification':
            labels = torch.Tensor([eval(i) for i in labels]).type(torch.float)
        else:
            if self.type_ == 'train':
                self.plot_data_info(labels, args)
            labels = torch.Tensor(labels).type(torch.long)

        data['labels'] = labels
        print('输入例子')
        print(sentences[0] if isinstance(sentences[0], str) else sentences[0][0])
        for k, v in data.items():
            print(k)
            print(v[0])
        print(f"实际序列转换后的长度为{len(data['input_ids'][0])}, 设置最长为{args.max_seq_len}")

        return data


if __name__ == '__main__':
    from transformers import BertTokenizer
    from torch.utils.data import DataLoader

    bert_tokenizer = BertTokenizer.from_pretrained(bert_path_or_name)
    dataset = DataPrecessForSentence(bert_tokenizer, args)

    for i in dataset:
        print(i)
        break

    d = DataLoader(dataset, batch_size=20)

    for ii, i in enumerate(d):
        print(i)
        print(ii)
        break
