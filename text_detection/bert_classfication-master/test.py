import argparse
import pandas as pd
import torch
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
import seaborn as sns
import matplotlib.pyplot as plt
from sys import platform
from torch.utils.data import DataLoader
from transformers import RobertaTokenizer, BertTokenizer
# from model import BertModel
from utils import test, eval_object
from dataset import DataPrecessForSentence
from config import *


def get_model_tokenizer(args):
    ClassifyClass = eval_object(model_dict[args.model][1])
    TokenizerClass = eval_object(model_dict[args.model][0])
    model = ClassifyClass.from_pretrained(args.pretrain_dir)
    model = model.to(args.device)
    tokenizer = TokenizerClass.from_pretrained(args.pretrain_dir)
    return model, tokenizer


def set_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='bert', type=str, required=False, help='使用什么模型')
    parser.add_argument('--problem_type', default='single_label_classification', type=str, required=False,
                        help='单标签分类还是多标签分类')
    parser.add_argument('--dir_name', default='fraud_text', type=str, required=False,
                        help='训练集存放目录,里面包含train.csv test.csv dev.csv')
    parser.add_argument('--batch_size', default=64, type=int, required=False, help='训练的batch size')
    parser.add_argument('--max_seq_len', default=150, type=int, required=False, help='训练时，输入数据的最大长度')
    parser.add_argument('--text_col_name', default='text', type=str, required=False, help='train.csv文本列名字')
    parser.add_argument('--class_col_name', default='class', type=str, required=False, help='train.csv标签列名字')
    parser.add_argument('--csv_sep', default=',', type=str, required=False, help='csv列间隔')
    parser.add_argument('--csv_encoding', default='utf-8', type=str, required=False, help='csv编码格式')
    args = parser.parse_args()
    return args


def init(args):
    pretrain_dir = f'./models/{args.dir_name}/{args.model}/'
    test_pred_out = f"data/{args.dir_name}/test_data_predict.csv"
    test_file = f"data/{args.dir_name}/test.csv"
    json_dict = f"data/{args.dir_name}/class.txt"

    with open(json_dict, 'r', encoding='utf-8') as f:
        classes = f.readlines()
    label2id = {label.strip(): i for i, label in enumerate(classes)}
    id2label = {v: k for k, v in label2id.items()}
    num_labels = len(classes)
    print(f"num_labels 是{num_labels}")

    args.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    args.pretrain_dir = pretrain_dir
    args.test_pred_out = test_pred_out
    args.test_file = test_file
    args.id2label = id2label
    args.label2id = label2id
    args.num_labels = num_labels


def plot_confusion_matrix(cm, labels, output_file):
    # 画混淆矩阵
    plt.figure(figsize=(10, 7))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title('Confusion Matrix')
    plt.savefig(output_file)
    plt.close()


def main():
    args = set_args()
    init(args)
    model, tokenizer = get_model_tokenizer(args)

    test_data = DataPrecessForSentence(tokenizer, args, 'test')
    test_loader = DataLoader(test_data, shuffle=False, batch_size=args.batch_size)

    print(20 * "=", " Testing model on device: {} ".format(args.device), 20 * "=")
    batch_time, total_time, accuracy, all_labels, all_pred = test(model, test_loader, args)

    print(
        "\n-> Average batch processing time: {:.4f}s, total test time: {:.4f}s, accuracy: {:.4f}%\n".format(batch_time,
                                                                                                            total_time,
                                                                                                            accuracy * 100))

    df = pd.read_csv(args.test_file, engine='python', encoding=args.csv_encoding, on_bad_lines='skip')
    df['pred'] = [i.cpu().numpy() for i in all_pred]

    if args.problem_type == 'multi_label_classification':
        df['all_pred'] = [[args.id2label[jj] for jj, j in enumerate(i) if j] for i in all_pred]
    else:
        df['pred'] = df['pred'].apply(int)

    # 计算混淆矩阵
    cm = confusion_matrix(df[args.class_col_name], df['pred'])

    # 使用模型名来生成混淆矩阵文件名
    cm_output_file = f"data/{args.dir_name}/confusion_matrix_{args.model}.png"
    plot_confusion_matrix(cm, list(args.id2label.values()), cm_output_file)

    # 使用模型名来生成预测结果文件名
    test_pred_out_file = f"data/{args.dir_name}/test_data_predict_{args.model}.csv"
    df.to_csv(test_pred_out_file, index=False, encoding='utf-8')


if __name__ == "__main__":
    main()
