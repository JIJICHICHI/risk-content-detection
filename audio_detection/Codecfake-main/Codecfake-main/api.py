import requests
import os
import flask_restplus

# 测试配置
API_URL = "http://localhost:5000"  # 确保与Flask应用端口一致
AUDIO_TEST_FILE = "test_audio.wav"  # 替换为实际测试音频文件路径


def test_text_analysis():
    print("测试文本分析接口...")

    # 测试正常文本
    normal_text = "今天天气不错，适合出门散步。"
    response = requests.post(
        f"{API_URL}/text_fraud",
        json={"text": normal_text}
    )
    print(f"响应状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"BERT分类: {data['bert_prediction']}")
        print(f"DeepSeek分析: {data['deepseek_analysis'][:100]}...")  # 显示前100字符
    else:
        print(f"错误信息: {response.text}")

    # 测试诈骗文本
    fraud_text = "你好，我是公安局的，你的账户涉嫌洗钱，请立即转账到安全账户。"
    response = requests.post(
        f"{API_URL}/text_fraud",
        json={"text": fraud_text}
    )
    print(f"响应状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"BERT分类: {data['bert_prediction']}")
        print(f"DeepSeek分析: {data['deepseek_analysis'][:100]}...")
    else:
        print(f"错误信息: {response.text}")

    # 测试缺少text字段
    response = requests.post(
        f"{API_URL}/text_fraud",
        json={}
    )
    print(f"缺少text字段测试状态码: {response.status_code}")
    print(f"错误信息: {response.text}")
    print("-" * 50)


def test_audio_analysis():
    print("测试音频分析接口...")

    # 测试有效音频文件
    if os.path.exists(AUDIO_TEST_FILE):
        with open(AUDIO_TEST_FILE, "rb") as f:
            files = {"audio": f}
            response = requests.post(
                f"{API_URL}/audio_fraud",
                files=files
            )
            print(f"响应状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"语音转文字: {data['text'][:100]}...")
                print(f"BERT分类: {data['bert_prediction']}")
                print(f"DeepSeek分析: {data['deepseek_analysis'][:100]}...")
            else:
                print(f"错误信息: {response.text}")
    else:
        print(f"错误: 测试音频文件 {AUDIO_TEST_FILE} 不存在")

    # 测试无效文件类型
    with open("test.txt", "w") as f:
        f.write("这是一个文本文件")
    with open("test.txt", "rb") as f:
        files = {"audio": f}
        response = requests.post(
            f"{API_URL}/audio_fraud",
            files=files
        )
        print(f"无效文件类型测试状态码: {response.status_code}")
        print(f"错误信息: {response.text}")
    os.remove("test.txt")
    print("-" * 50)


if __name__ == "__main__":
    test_text_analysis()
    test_audio_analysis()