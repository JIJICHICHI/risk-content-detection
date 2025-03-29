import pandas as pd
import os
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

# 读取并合并数据集
file_paths = {
    "label00-last.csv": 0,
    "label01-last.csv": 1,
    "label02-last.csv": 2,
    "label03-last.csv": 3,
    "label04-last.csv": 4
}

data = []
for file, label in file_paths.items():
    df = pd.read_csv(file, names=["text", "label"])

    df["label"] = label  # 统一数值标签
    data.append(df)

data = pd.concat(data, ignore_index=True)

# 按类别均衡采样，划分数据集
train, temp = train_test_split(data, test_size=0.2, stratify=data['label'], random_state=42)
val, test = train_test_split(temp, test_size=0.5, stratify=temp['label'], random_state=42)

# 保存划分后的数据集 (修正class和text的内容)
train.to_csv("train.csv", index=False, header=["text", "class"])
val.to_csv("dev.csv", index=False, header=["text", "class"])
test.to_csv("test.csv", index=False, header=["text", "class"])

# 统计每个数据集中不同类别的样本数量
def plot_distribution(dataset, title, filename):
    class_counts = dataset['label'].value_counts().sort_index()
    plt.bar(class_counts.index, class_counts.values, alpha=0.7, label=title)
    for i, v in enumerate(class_counts.values):
        plt.text(i, v + 5, str(v), ha='center', fontsize=10)
    plt.xlabel("Class")
    plt.ylabel("Count")
    plt.title(title)
    plt.xticks(class_counts.index)
    plt.legend()
    # Save the plot to a file
    plt.savefig(filename)
    plt.close()

# Plot and save distributions
plt.figure(figsize=(12, 4))
plot_distribution(train, "Training Set Distribution", "train_distribution.png")
plot_distribution(val, "Validation Set Distribution", "dev_distribution.png")
plot_distribution(test, "Test Set Distribution", "test_distribution.png")
