from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from openai import OpenAI
import whisper
from pydub import AudioSegment
import os

from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)  # 允许跨域并支持凭证

# ================= 初始化所有模型 =================

# 1. 初始化DeepSeek
deepseek_client = OpenAI(
    api_key="sk-a962c65e8bd74286b590b57345b9f0f9",  # 注意使用ds-开头的密钥
    base_url="https://api.deepseek.com/"
)

# 2. 加载BERT分类模型
bert_model_path = "./models/fraud_text/roberta"
bert_tokenizer = AutoTokenizer.from_pretrained(bert_model_path)
bert_model = AutoModelForSequenceClassification.from_pretrained(bert_model_path)
bert_model.eval()

# 3. 加载Whisper语音识别模型
whisper_model = whisper.load_model("small")  # 中文推荐使用small或medium


# ================= 工具函数 =================

def convert_audio_to_wav(input_path):
    """统一转换为WAV格式"""
    if input_path.endswith(".wav"):
        return input_path

    audio = AudioSegment.from_file(input_path)
    wav_path = os.path.splitext(input_path)[0] + ".wav"
    audio.export(wav_path, format="wav")
    return wav_path


def transcribe_audio(audio_path):
    """语音转文字"""
    result = whisper_model.transcribe(
        audio_path,
        language="zh",
        initial_prompt="以下是普通话对话内容"  # 提高中文识别精度
    )
    return result["text"]


# ================= 核心功能 =================

def analyze_text(text):
    """文本分析入口"""
    # BERT分类
    inputs = bert_tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = bert_model(**inputs)
    bert_pred = torch.argmax(outputs.logits).item()

    # DeepSeek分析
    ds_response = deepseek_client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是有20年经验的反诈专家，需要分析以下内容："},
            {"role": "user",
             "content": f"请分析是否涉及：1.公安诈骗 2.贷款诈骗 3.冒充客服 4.冒充领导/熟人 5.其他诈骗\n文本内容：{text}"}
        ],
        temperature=0.3  # 降低随机性
    )

    return {
        "bert_category": ["正常", "公安诈骗", "贷款诈骗", "冒充客服", "冒充领导"][bert_pred],
        "ai_analysis": ds_response.choices[0].message.content
    }


# ================= API接口 =================
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    return response

@app.route('/analyze/audio', methods=['POST'])
def analyze_audio():
    try:
        # 1. 接收并保存文件
        if 'audio' not in request.files:
            return jsonify({"error": "未上传音频文件"}), 400

        audio_file = request.files['audio']
        upload_dir = "./tmp_uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, audio_file.filename)
        audio_file.save(file_path)
        print(f"音频文件已保存到: {file_path}")  # 添加这行代码

        # 2. 音频转文字
        wav_path = convert_audio_to_wav(file_path)
        print(f"转换后的WAV文件路径: {wav_path}")  # 添加这行代码
        text = transcribe_audio(wav_path)
        print(f"语音转文字结果: {text}")  # 添加这行代码

        # 3. 分析文本
        result = analyze_text(text)

        # 4. 清理临时文件
        os.remove(file_path)
        if file_path != wav_path:  # 删除转换后的文件
            os.remove(wav_path)

        return jsonify({
            "transcribed_text": text,
            "analysis": result
        })

    except Exception as e:
        print(f"发生异常: {e}")  # 添加这行代码
        return jsonify({"error": str(e)}), 500


@app.route('/analyze/text', methods=['POST'])
def analyze_text_api():
    """纯文本分析接口（保留原有功能）"""
    data = request.get_json()
    if 'text' not in data:
        return jsonify({"error": "缺少文本内容"}), 400

    try:
        result = analyze_text(data['text'])
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)