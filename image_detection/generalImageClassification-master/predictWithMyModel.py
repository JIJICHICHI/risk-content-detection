import timeit
import numpy as np
import base64
from io import BytesIO
import logging
from keras.models import load_model
from keras.preprocessing import image
from keras import backend as K
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True


if K.image_data_format() == 'channels_first':
    input_shape = (3, 224, 224)
else:
    input_shape = (224, 224, 3)

## 定义log
logger = logging.getLogger(__name__)

# 返回一个编译好的模型
# 与之前那个相同
print("开始加载模型：")
logger.info("开始加载模型")
starttime = timeit.default_timer()
model = load_model('data/modelFile/my_model03.h5')
endtime = timeit.default_timer()
print("模型加载完成，用时为：", endtime - starttime)
logger.info("模型加载完成，用时为：%s", endtime - starttime)




def predictWithImagePath(img_path):
    """
    根据输入图像path，来分析图像，并作出分类。
    :param img_path:图像路径
    :return:图像的类别
    """
    # 加载图像
    img = image.load_img(img_path, target_size = input_shape)
    # 图像预处理
    x = image.img_to_array(img) / 255.0 # 与训练一致
    x = np.expand_dims(x, axis=0)

    # 对图像进行分类
    preds = model.predict(x) # Predicted: [[1.0000000e+00 1.4072199e-33 1.0080164e-22 3.4663230e-32]]
    print('Predicted:', preds)     # 输出预测概率
    predicted_class_indices = np.argmax(preds,axis=1)
    print('predicted_class_indices:', predicted_class_indices) # 输出预测类别的int

    labels = {'neutral': 0, 'political': 1, 'porn': 2, 'terrorism': 3}
    labels = dict((v, k) for k, v in labels.items())
    predicted_class = labels[predicted_class_indices[0]]
    # predictions = [labels[k] for k in predicted_class_indices]
    print("predicted_class :", predicted_class)
    return predicted_class, preds[0][predicted_class_indices[0]]

def predictWithImageBase64(imageBase64String):
    """
    根据输入图像Base64，来分析图像，并作出分类。
    :param ImageBase64:图像Base64编码
    :return:图像的类别
    """
    try:
        # 加载图像 base64
        imageBase64String = imageBase64String.split(',')
        if (len(imageBase64String) > 1):
            imageBase64String = imageBase64String[1]
        else:
            imageBase64String = imageBase64String[0]

        imageBinaryData = base64.b64decode(imageBase64String) # 解码base64
        imageData = BytesIO(imageBinaryData)  # 在内存中读取

        img = image.load_img(imageData, target_size = input_shape)# 读取图片，并压缩至指定大小
        # 图像预处理
        x = image.img_to_array(img) / 255.0 # 与训练一致
        x = np.expand_dims(x, axis=0)
    except:
        return "98", "失败，解析 imageBase64String 参数的过程失败。",0,0


    # 对图像进行分类
    try:
        preds = model.predict(x) # Predicted: [[1.0000000e+00 1.4072199e-33 1.0080164e-22 3.4663230e-32]]
    except:
        return "98", "失败，模型运行失败。",0,0
    print('Predicted:', preds)     # 输出预测概率
    logger.info('Predicted:%s', preds)
    predicted_class_indices = np.argmax(preds,axis=1)
    print('predicted_class_indices:', predicted_class_indices) # 输出预测类别的int
    logger.info('predicted_class_indices:%s', predicted_class_indices)

    labels = {'neutral': 0, 'political': 1, 'porn': 2, 'terrorism': 3}
    labels = dict((v, k) for k, v in labels.items())
    predicted_class = labels[predicted_class_indices[0]]
    # predictions = [labels[k] for k in predicted_class_indices]
    print("predicted_class :", predicted_class)
    logger.info('predicted_class:%s', predicted_class)

    return "00", "成功",predicted_class,preds[0][predicted_class_indices[0]]


if __name__ == '__main__':
    img_path_list = [
        "data/validation/neutral/[www.google.com][1989].jpg",  # neutral
        "data/validation/neutral/[www.google.com][396].jpg",  # neutral
        "data/validation/political/[www.google.com][440].jpg",  # political
        "data/validation/political/[www.google.com][466].jpg",  # political
        "data/validation/porn/[www.google.com][16973].jpg",  # porn
        "data/validation/porn/[www.google.com][10382].jpg",  # porn
        "data/validation/porn/[www.google.com][18585].jpg",  # porn
        "data/validation/terrorism/[www.google.com][601].jpg",  # terrorism
        "data/validation/terrorism/[www.google.com][3791].jpg",  # terrorism
        "data/validation/terrorism/[www.google.com][5399].jpg",  # terrorism
    ]
    print("开始预测：")

    for i in img_path_list:
        starttime = timeit.default_timer()
        print(predictWithImagePath(i))
        endtime = timeit.default_timer()
        print("单次调用模型预测时间为：", endtime - starttime)


    # 使用base64 处理
    base64String = "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"
    starttime = timeit.default_timer()
    print(predictWithImageBase64(base64String))
    endtime = timeit.default_timer()
    print("单次调用模型预测时间为：", endtime - starttime)