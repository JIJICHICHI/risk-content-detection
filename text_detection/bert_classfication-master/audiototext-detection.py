from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import openai
import speech_recognition as sr
from pydub import AudioSegment
import io

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
        messages=[{
            "role": "system",
            "content": "你是一个安全专家，帮助分析诈骗内容"
        }, {
            "role": "user",
            "content": f"请分析这段话是否涉及以下诈骗，公安诈骗，贷款诈骗，冒充客服，冒充领导/熟人，或者存在其他诈骗手段，并解释理由：{text}"
        }],
        stream=False
    )
    return response.choices[0].message.content  # 返回 DeepSeek 生成的解释

# 语音转文本功能
def audio_to_text(audio_file):
    # 使用 SpeechRecognition 进行语音识别
    recognizer = sr.Recognizer()

    # 打开音频文件
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        try:
            # 使用 Google Web Speech API 进行语音识别
            text = recognizer.recognize_google(audio_data, language='zh-CN')
            return text
        except sr.UnknownValueError:
            return "无法识别语音"
        except sr.RequestError as e:
            return f"语音识别服务请求失败: {e}"

# Flask 应用初始化
app = Flask(__name__)

# 5️⃣ 创建 API 接口
@app.route('/audio_fraud', methods=['POST'])
def classify_text():
    if 'audio' not in request.files:
        return jsonify({'error': 'Missing audio file'}), 400

    audio_file = request.files['audio']

    # 将音频文件转为文本
    text_to_analyze = audio_to_text(audio_file)

    # 使用 BERT 分类
    bert_prediction = classify_with_bert(text_to_analyze)
    category_map = {
        0: "正常文本",
        1: "公安诈骗",
        2: "贷款诈骗",
        3: "冒充客服",
        4: "冒充领导/熟人"
    }
    category = category_map.get(bert_prediction, "未知类别")

    # 使用 DeepSeek 分析
    deepseek_analysis = analyze_with_deepseek(text_to_analyze)

    return jsonify({
        'bert_prediction': category,
        'deepseek_analysis': deepseek_analysis
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
