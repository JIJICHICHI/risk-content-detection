from flask import Flask, request, jsonify, Response
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from openai import OpenAI
import time
import json
from flask_cors import CORS
import whisper  # 导入 Whisper 模型
import tempfile
import os

app = Flask(__name__)
CORS(app)

# 1️⃣ DeepSeek API
client = OpenAI(api_key="sk-a962c65e8bd74286b590b57345b9f0f9", base_url="https://api.deepseek.com")

# 2️⃣ 加载微调好的 BERT 模型
bert_model_path = "./models/fraud_text/roberta"
tokenizer = AutoTokenizer.from_pretrained(bert_model_path)
model = AutoModelForSequenceClassification.from_pretrained(bert_model_path)
model.eval()

# 加载 Whisper 模型（这里使用 base 模型，可根据需要调整）
whisper_model = whisper.load_model("base")


# BERT 诈骗分类
def classify_with_bert(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    prediction = torch.argmax(logits, dim=1).item()
    return prediction


# DeepSeek 诈骗分析（流式输出） —— 保持原有接口
def analyze_with_deepseek_stream(text):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个安全专家，帮助分析诈骗内容"},
            {"role": "user", "content": f"请分析这段话是正常文本还是涉及以下诈骗，公安诈骗，贷款诈骗，冒充客服，冒充领导/熟人，或者存在其他诈骗手段，并解释风险点:\n{text}"}
        ],
        stream=True
    )

    full_response = ""
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            full_response += content
            # 以 NDJSON 格式流式返回
            yield json.dumps({
                "deepseek_analysis": full_response,
                "complete": False
            }) + "\n"

    yield json.dumps({
        "deepseek_analysis": full_response,
        "complete": True,
        "time_taken": 0
    }) + "\n"


# 诈骗分类接口（BERT）
@app.route('/text_fraud_bert', methods=['POST'])
def classify_fraud_bert():
    data = request.get_json()
    if 'text' not in data:
        return jsonify({"error": "缺少 'text' 参数"}), 400

    test_text = data['text']
    start_time = time.time()

    # BERT 进行分类
    bert_prediction = classify_with_bert(test_text)
    category_map = {0: "正常文本", 1: "公安诈骗", 2: "贷款诈骗", 3: "冒充客服", 4: "冒充领导/熟人"}
    category = category_map.get(bert_prediction, "未知类别")

    elapsed_time = time.time() - start_time

    return jsonify({
        "bert_category": category,
        "time_taken": elapsed_time
    })


# 诈骗分析接口（DeepSeek，流式输出）
@app.route('/text_fraud_deepseek', methods=['POST'])
def classify_fraud_deepseek():
    data = request.get_json()
    if 'text' not in data:
        return jsonify({"error": "缺少 'text' 参数"}), 400

    test_text = data['text']

    return Response(
        analyze_with_deepseek_stream(test_text),
        content_type='application/x-ndjson'
    )


# 新增：音频转文本并进行诈骗分析接口
@app.route('/audio_fraud_analysis', methods=['POST'])
def audio_fraud_analysis():
    # 检查是否包含音频文件
    if 'audio' not in request.files:
        return jsonify({"error": "缺少 'audio' 文件"}), 400

    audio_file = request.files['audio']

    # 保存音频到临时文件（注意：根据上传文件格式，此处可适当设置后缀，比如 .wav 或 .mp3）
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        audio_file.save(tmp.name)
        tmp_path = tmp.name

    try:
        # 使用 Whisper 进行音频转文本
        result = whisper_model.transcribe(tmp_path)
        transcribed_text = result.get("text", "").strip()

        # 使用 BERT 对转录文本进行诈骗分类
        bert_prediction = classify_with_bert(transcribed_text)
        category_map = {0: "正常文本", 1: "公安诈骗", 2: "贷款诈骗", 3: "冒充客服", 4: "冒充领导/熟人"}
        category = category_map.get(bert_prediction, "未知类别")

        # 使用 DeepSeek 进行诈骗风险分析（非流式方式）
        deepseek_response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个安全专家，帮助分析诈骗内容"},
                {"role": "user", "content": f"请分析这段话是正常文本还是涉及以下诈骗，公安诈骗，贷款诈骗，冒充客服，冒充领导/熟人，或者存在其他诈骗手段，并解释风险点:\n{transcribed_text}"}
            ],
            stream=False
        )
        deepseek_text = deepseek_response.choices[0].message.content

        # 返回音频转文本和分析结果
        return jsonify({
            "transcribed_text": transcribed_text,
            "bert_category": category,
            "deepseek_analysis": deepseek_text
        })
    finally:
        # 删除临时文件
        os.remove(tmp_path)


if __name__ == '__main__':
    app.run(debug=True)
