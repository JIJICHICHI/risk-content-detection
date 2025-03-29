import os
import torch
import librosa
from flask import Flask, request, jsonify
from model import W2VAASIST
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2Model
import torch.nn.functional as F
import soundfile as sf
from flask_cors import CORS




def pad_dataset(wav, target_length=64600):
    waveform = wav.squeeze(0)
    if waveform.dim() == 1:
        waveform = waveform.unsqueeze(0)
    waveform_len = waveform.size(-1)
    if waveform_len >= target_length:
        return waveform[:, :target_length]
    num_repeats = int(target_length / waveform_len) + 1
    padded_waveform = torch.tile(waveform, (1, num_repeats))[:, :target_length]
    return padded_waveform

def extract_features(audio_path):
    audio, sr = librosa.load(audio_path, sr=16000, mono=True)
    waveform = torch.FloatTensor(audio).unsqueeze(0).unsqueeze(0)
    padded_waveform = pad_dataset(waveform)
    processor = Wav2Vec2FeatureExtractor.from_pretrained("./pretrained_models/wav2vec2-xls-r-300m")
    inputs = processor(
        padded_waveform.squeeze().numpy(),
        sampling_rate=16000,
        return_tensors="pt",
        padding=True,
        return_attention_mask=True
    )
    model = Wav2Vec2Model.from_pretrained("./pretrained_models/wav2vec2-xls-r-300m")
    model.config.output_hidden_states = True
    with torch.no_grad():
        outputs = model(**inputs)
        features = outputs.hidden_states[5]
    return features.unsqueeze(1).permute(0, 1, 3, 2)

def load_model(model_path, device='cuda'):
    model = W2VAASIST()
    loaded = torch.load(model_path, map_location=device)
    if isinstance(loaded, dict):
        state_dict = loaded
    else:
        model = loaded
        model = model.to(device)
        model.eval()
        return model
    if 'module.' in list(state_dict.keys())[0]:
        state_dict = {k.replace('module.', ''): v for k, v in state_dict.items()}
    model.load_state_dict(state_dict)
    model = model.to(device)
    model.eval()
    return model

def inference(model, features, device='cuda', threshold=0.5):
    with torch.no_grad():
        features = features.to(device)
        _, outputs = model(features)
        probabilities = F.softmax(outputs, dim=1)
        spoof_prob = probabilities[:, 1].item()
        return "深度伪造音频" if spoof_prob > threshold else "真实音频", spoof_prob

def sliding_window_detection(audio_path, model, window_size=3.0, step_size=1.0, sr=16000, device='cuda'):
    audio, _ = librosa.load(audio_path, sr=sr, mono=True)
    results = []
    total_duration = len(audio) / sr
    start = 0
    while start < total_duration:
        end = min(start + window_size, total_duration)
        segment = audio[int(start * sr):int(end * sr)]
        temp_path = "temp.wav"

        sf.write(temp_path, segment, sr)

        features = extract_features(temp_path)
        result, confidence = inference(model, features, device)
        results.append({"start": start, "end": end, "result": result, "confidence": confidence})
        start += step_size
    return results

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model_path = './pretrained_model/codec_w2v2aasist/anti-spoofing_feat_model.pt'
model = load_model(model_path, device)

@app.route('/detect', methods=['POST'])
def detect():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    filename = "uploaded.wav"
    file.save(filename)
    results = sliding_window_detection(filename, model, device=device)
    os.remove(filename)
    return jsonify({"results": results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
    CORS(app, resources={r"/*": {"origins": "*"}})  # 允许所有源（生产环境需限制）
