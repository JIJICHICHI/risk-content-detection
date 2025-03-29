import torch
import librosa
import torchaudio
from model import W2VAASIST
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2Model
import torch.nn.functional as F
import os


# 与preprocess.py保持一致的预处理逻辑
def pad_dataset(wav, target_length=64600):
    """确保与训练时完全相同的填充逻辑"""
    waveform = wav.squeeze(0)
    if waveform.dim() == 1:
        waveform = waveform.unsqueeze(0)

    waveform_len = waveform.size(-1)
    if waveform_len >= target_length:
        return waveform[:, :target_length]

    # 计算需要重复的次数（与preprocess.py一致）
    num_repeats = int(target_length / waveform_len) + 1
    padded_waveform = torch.tile(waveform, (1, num_repeats))[:, :target_length]
    return padded_waveform


def extract_features(audio_path):
    """与preprocess.py严格一致的特征提取流程"""
    # 加载音频（保持与训练相同的参数）
    audio, sr = librosa.load(audio_path, sr=16000, mono=True)

    # 转换为tensor并添加batch维度
    waveform = torch.FloatTensor(audio).unsqueeze(0).unsqueeze(0)  # [1, 1, T]

    # 填充处理（与训练时一致）
    padded_waveform = pad_dataset(waveform)

    # 初始化处理器（使用与训练相同的配置）
    processor = Wav2Vec2FeatureExtractor.from_pretrained("./pretrained_models/wav2vec2-xls-r-300m")


    # 生成输入特征（严格对齐generate_score.py的处理方式）
    inputs = processor(
        padded_waveform.squeeze().numpy(),
        sampling_rate=16000,
        return_tensors="pt",
        padding=True,
        return_attention_mask=True
    )

    # 加载模型（使用与训练相同的hidden layer）
    model = Wav2Vec2Model.from_pretrained("./pretrained_models/wav2vec2-xls-r-300m")
    model.config.output_hidden_states = True

    with torch.no_grad():
        outputs = model(**inputs)
        # 使用第5层隐藏状态（与generate_score.py一致）
        features = outputs.hidden_states[5]  # [batch_size, seq_len, 1024]

    # 调整维度匹配模型输入 [batch, 1, seq_len, feature_dim]
    return features.unsqueeze(1).permute(0, 1, 3, 2)  # 匹配W2VAASIST的输入维度


def load_model(model_path, device='cuda'):
    """修正模型加载方式"""
    model = W2VAASIST()

    # 加载模型
    loaded = torch.load(model_path, map_location=device)

    # 检查loaded是否为状态字典
    if isinstance(loaded, dict):
        print("加载的是模型状态字典")
        state_dict = loaded
    else:
        print("加载的是整个模型")
        model = loaded  # 如果是整个模型，直接使用
        model = model.to(device)
        model.eval()
        return model

    if 'module.' in list(state_dict.keys())[0]:
        # 处理多GPU训练保存的模型
        state_dict = {k.replace('module.', ''): v for k, v in state_dict.items()}

    model.load_state_dict(state_dict)
    model = model.to(device)
    model.eval()
    return model


def inference(model, features, device='cuda', threshold=0.5):
    """严格对齐训练时的前向过程"""
    with torch.no_grad():
        features = features.to(device)
        # 执行与main_train.py一致的前向计算
        _, outputs = model(features)

        # 使用softmax概率（与evaluate_score.py一致）
        probabilities = F.softmax(outputs, dim=1)
        spoof_prob = probabilities[:, 1].item()  # 假设第1维是伪造概率

        # 阈值决策（根据训练集调整）
        return "深度伪造音频" if spoof_prob > threshold else "真实音频", spoof_prob


if __name__ == "__main__":
    # 配置参数（与训练配置对齐）
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model_path = './pretrained_model/codec_w2v2aasist/anti-spoofing_feat_model.pt'
    audio_path = '7.wav'

    # 加载模型
    model = load_model(model_path, device)

    # 特征提取
    features = extract_features(audio_path)
    print(f"特征维度：{features.shape}")  # 应为[batch, 1, 1024, seq_len]

    # 执行推理
    result, confidence = inference(model, features, device)
    print(f"检测结果: {result} (置信度: {confidence:.4f})")