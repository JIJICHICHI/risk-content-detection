from tensorflow.keras.applications.inception_v3 import InceptionV3
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras import backend as K
from tensorflow.keras.utils import load_img, img_to_array
import numpy as np
from PIL import ImageFile


# 解决加载部分图像截断的问题
ImageFile.LOAD_TRUNCATED_IMAGES = True

### 超参数：
# 图像尺寸
img_width, img_height = 224, 224

# 数据路径
train_data_dir = 'data/train'
validation_data_dir = 'data/validation'

# 数据集样本数量
nb_train_samples = 477
nb_validation_samples = 12

# 训练参数
epochs = 20
batch_size = 32

# 根据图像数据格式确定输入形状
if K.image_data_format() == 'channels_first':
    input_shape = (3, img_width, img_height)
else:
    input_shape = (img_width, img_height, 3)

# 构建不带分类器的预训练 InceptionV3 模型
base_model = InceptionV3(weights='imagenet', include_top=False, input_shape=input_shape)

# 添加全局平均池化层
x = base_model.output
x = GlobalAveragePooling2D()(x)

# 添加一个全连接层
x = Dense(512, activation='relu')(x)

# 添加分类器层，4个类别
predictions = Dense(4, activation='softmax')(x)

# 构建完整模型
model = Model(inputs=base_model.input, outputs=predictions)

# 锁住 InceptionV3 的所有卷积层
for layer in base_model.layers:
    layer.trainable = False

# 编译模型
model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=["accuracy"])

### 数据扩充
# 训练数据扩充
train_datagen = ImageDataGenerator(
    rescale=1. / 255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True
)

# 验证数据扩充
valid_datagen = ImageDataGenerator(rescale=1. / 255)

# 生成训练数据
train_generator = train_datagen.flow_from_directory(
    train_data_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode='categorical'
)

# 打印类别索引
print("Train Class Indices:", train_generator.class_indices)

# 生成验证数据
validation_generator = valid_datagen.flow_from_directory(
    validation_data_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode='categorical'
)

# 打印类别索引
print("Validation Class Indices:", validation_generator.class_indices)

### 训练模型
print("开始训练：")
model.fit(
    train_generator,
    steps_per_epoch=nb_train_samples // batch_size,
    epochs=epochs,
    validation_data=validation_generator,
    validation_steps=max(1, nb_validation_samples // batch_size)
)

# 保存模型
model.save('data/modelFile/my_model.h5')
print("保存模型成功。")

### 使用模型进行预测
print("使用模型预测：-----------")
img_path = 'data/validation/political/[www.google.com][440].jpg'  # 替换为测试图像路径

# 加载图像
img = load_img(img_path, target_size=(img_width, img_height))

# 预处理图像
x1 = img_to_array(img) / 255.0
x1 = np.expand_dims(x1, axis=0)

# 预测
preds = model.predict(x1)
print('Predicted:', preds)

# 获取预测类别索引
predicted_class_indices = np.argmax(preds, axis=1)

# 动态获取类别名称
labels = {v: k for k, v in train_generator.class_indices.items()}
predicted_class = labels[predicted_class_indices[0]]

print("Predicted Class:", predicted_class)
