from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from openai import OpenAI  # 使用 DeepSeek 的 SDK

# 1️⃣ 设置 DeepSeek API
client = OpenAI(api_key="sk-a962c65e8bd74286b590b57345b9f0f9", base_url="https://api.deepseek.com")

# 2️⃣ 加载你微调好的 BERT 模型
bert_model_path = "./models/fraud_text/roberta"  # 你的 BERT 训练好的路径
tokenizer = AutoTokenizer.from_pretrained(bert_model_path)
model = AutoModelForSequenceClassification.from_pretrained(bert_model_path)  # 假设是分类任务
model.eval()

# 3️⃣ BERT 进行诈骗分类
def classify_with_bert(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    prediction = torch.argmax(logits, dim=1).item()  # 取最高分的类别
    return prediction  # 返回分类结果

# 4️⃣ DeepSeek 进行诈骗分析
def analyze_with_deepseek(text):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个安全专家，帮助分析诈骗内容"},
            {"role": "user", "content": f"请分析这段话是否涉及以下诈骗，公安诈骗，贷款诈骗，冒充客服，冒充领导/熟人，或者存在其他诈骗手段，并解释理由：{text}"}
        ],
        stream=False
    )
    return response.choices[0].message.content  # 返回 DeepSeek 生成的解释

# 5️⃣ 测试：输入诈骗文本
test_text = "你好，我是下陆公安分局的警察。我打电话是因为我们发现一个名叫的嫌疑人使用了他名下的一张卡进行洗钱活动。我们怀疑这张卡可能与您的身份信息有关。为了调查此事，我们需要您的帮助。请添加我们的QQ好友，我们会给您发送一份“通缉令”。如果您确认这是您的身份证号，我们将进一步调查此事。如果您需要进一步的信息或帮助，请随时与我们联系。谢谢您的配合。"  # 示例诈骗文本

# 先用 BERT 分类
bert_prediction = classify_with_bert(test_text)
category_map = {0: "正常文本", 1: "公安诈骗", 2: "贷款诈骗", 3: "冒充客服", 4: "冒充领导/熟人"}  # 你自己的类别映射
category = category_map.get(bert_prediction, "未知类别")
print(f"BERT 预测类别: {category}")

# 再用 DeepSeek 分析诈骗手法
deepseek_analysis = analyze_with_deepseek(test_text)
print(f"DeepSeek 分析结果: {deepseek_analysis}")
