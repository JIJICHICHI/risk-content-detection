from flask import Flask, request, jsonify
import torch
import torchaudio
import numpy as np
import os
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2Model
from model import W2VAASIST  # 根据实际使用的模型选择
import tempfile

app = Flask(__name__)

# 初始化配置
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_PATH = "./pretrained_model/cotrain_w2v2aasist_CSAM/anti-spoofing_feat_model.pt"
WAV2VEC_PATH = "facebook/wav2vec2-xls-r-300m"  # 使用Hugging Face官方模型名称
# 加载特征提取器和模型
processor = Wav2Vec2FeatureExtractor.from_pretrained(WAV2VEC_PATH)
wav2vec_model = Wav2Vec2Model.from_pretrained(WAV2VEC_PATH).to(DEVICE)
wav2vec_model.config.output_hidden_states = True

# 初始化检测模型
model = W2VAASIST().to(DEVICE)
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model.eval()


def pad_waveform(waveform):
    """音频填充处理"""
    waveform_len = waveform.shape[-1]
    cut = 64600
    if waveform_len >= cut:
        return waveform[..., :cut]
    num_repeats = int(cut / waveform_len) + 1
    return torch.tile(waveform, (1, num_repeats))[..., :cut]


def extract_features(waveform):
    """特征提取"""
    waveform = pad_waveform(waveform)
    input_values = processor(
        waveform.numpy(),
        sampling_rate=16000,
        return_tensors="pt"
    ).input_values.to(DEVICE)

    with torch.no_grad():
        hidden_states = wav2vec_model(input_values).hidden_states[5]
    return hidden_states.cpu()


def predict(features):
    """模型推理"""
    with torch.no_grad():
        features = features.unsqueeze(0).transpose(2, 3).to(DEVICE)
        _, outputs = model(features)
        score = torch.softmax(outputs, dim=1)[0, 0].item()
    return score


@app.route('/detect', methods=['POST'])
def detect():
    """API端点"""
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    try:
        # 保存临时文件
        audio_file = request.files['audio']
        _, temp_path = tempfile.mkstemp(suffix=".wav")
        audio_file.save(temp_path)

        # 加载音频
        waveform, sr = torchaudio.load(temp_path)
        if sr != 16000:
            waveform = torchaudio.transforms.Resample(sr, 16000)(waveform)

        # 处理流程
        features = extract_features(waveform)
        score = predict(features)

        # 清理临时文件
        os.remove(temp_path)

        return jsonify({
            "score": score,
            "prediction": "spoof" if score > 0.5 else "bonafide"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)