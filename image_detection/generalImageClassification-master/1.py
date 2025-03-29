import requests
import base64

# 读取图片并转换为 Base64
with open("./data/validation/political/[www.google.com][466].jpg", "rb") as img_file:
    img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

# 发送 POST 请求
url = "http://127.0.0.1:8080/predict"
payload = {"image": img_base64}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)

# 输出结果
print("Response:", response.json())
