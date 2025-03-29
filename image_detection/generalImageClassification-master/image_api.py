from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import base64
from PIL import Image
import io
import predictWithMyModel  # 你的预测函数

app = Flask(__name__)
CORS(app)


@app.route('/detect_image', methods=['POST'])
def predict():
    start_time = time.time()

    try:
        data = request.json
        img_base64 = data.get("image")

        if not img_base64:
            return jsonify({
                "code": "01",
                "message": "未提供图片数据",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }), 400

        # 解码Base64并调用预测函数
        code, msg, predicted_class, probability = predictWithMyModel.predictWithImageBase64(img_base64)

        processing_time = time.time() - start_time

        if code == '00':
            return jsonify({
                "code": code,
                "predicted_class": predicted_class,
                "probability": float(probability),
                "processing_time": processing_time,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })
        else:
            return jsonify({
                "code": code,
                "message": msg,
                "processing_time": processing_time,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }), 500

    except Exception as e:
        return jsonify({
            "code": "99",
            "message": f"服务器错误: {str(e)}",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)