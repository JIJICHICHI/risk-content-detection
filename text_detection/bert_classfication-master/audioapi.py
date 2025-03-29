from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from openai import OpenAI
import speech_recognition as sr
from pydub import AudioSegment
import io

app = Flask(__name__)

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
            {"role": "user",
             "content": f"请分析这段话是否涉及以下诈骗，公安诈骗，贷款诈骗，冒充客服，冒充领导/熟人，或者存在其他诈骗手段，并解释理由：{text}"}
        ],
        stream=False
    )
    return response.choices[0].message.content  # 返回 DeepSeek 生成的解释


# 音频转文本
def audio_to_text(audio_file):
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)
    try:
        text = r.recognize_google(audio, language='zh-CN')
        return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print(f"请求错误: {e}")
        return None


@app.route('/text_fraud', methods=['POST'])
def classify_fraud():
    data = request.get_json()
    if 'text' not in data:
        return jsonify({"error": "Missing 'text' in the request body"}), 400
    test_text = data['text']

    # 先用 BERT 分类
    bert_prediction = classify_with_bert(test_text)
    category_map = {0: "正常文本", 1: "公安诈骗", 2: "贷款诈骗", 3: "冒充客服", 4: "冒充领导/熟人"}
    category = category_map.get(bert_prediction, "未知类别")

    # 再用 DeepSeek 分析诈骗手法
    deepseek_analysis = analyze_with_deepseek(test_text)

    return jsonify({
        "bert_prediction": category,
        "deepseek_analysis": deepseek_analysis
    })


@app.route('/audio_fraud', methods=['POST'])
def audio_fraud_detection():
    if 'audio' not in request.files:
        return jsonify({"error": "Missing 'audio' file in the request"}), 400

    audio_file = request.files['audio']
    try:
        # 保存音频文件到内存
        audio_content = audio_file.read()
        audio = AudioSegment.from_file(io.BytesIO(audio_content))
        audio.export('temp_audio.wav', format='wav')

        # 音频转文本
        text = audio_to_text('temp_audio.wav')
        if text is None:
            return jsonify({"error": "Could not convert audio to text"}), 400

        # 文本诈骗检测
        bert_prediction = classify_with_bert(text)
        category_map = {0: "正常文本", 1: "公安诈骗", 2: "贷款诈骗", 3: "冒充客服", 4: "冒充领导/熟人"}
        category = category_map.get(bert_prediction, "未知类别")
        deepseek_analysis = analyze_with_deepseek(text)

        return jsonify({
            "text": text,
            "bert_prediction": category,
            "deepseek_analysis": deepseek_analysis
        })
    except Exception as e:
        return jsonify({"error": f"An error occurred while processing the audio: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
