import pandas as pd

# 读取原始 CSV 文件
df = pd.read_csv("train.csv")

# 调整列顺序
df = df[["class", "text"]]

# 保存调整后的 CSV 文件
df.to_csv("train.csv", index=False)

print("CSV file has been modified successfully.")
