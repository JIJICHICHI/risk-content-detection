import io

import gradio as gr
import base64
import numpy as np
from PIL import Image
import predictWithMyModel  # 你原来用于预测的函数

# 定义图片处理函数
def predict_image(img):
    # 将PIL图像转化为base64格式
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    # 调用你的模型预测函数
    code, msg, predictedClass, probability = predictWithMyModel.predictWithImageBase64(img_base64)

    if code == '00':
        # 输出分类结果和置信度
        print(f"Predicted Class: {predictedClass}, Probability: {probability}")  # Debugging print
        return predictedClass, probability
    else:
        return "检测失败", msg



# 定义Gradio界面
iface = gr.Interface(
    fn=predict_image,  # 预测函数
    inputs=gr.Image(type="pil"),  # 用户输入为PIL格式图片
    outputs=[gr.Textbox(), gr.Textbox()],  # 输出预测结果和置信度
    title="图像内容违规检测",  # 应用标题
    description="上传图片进行内容检测，包括涉黄、涉政、涉恐等违规内容",  # 简单描述
)


iface.launch(share=False, server_name="127.0.0.1", server_port=8080)


