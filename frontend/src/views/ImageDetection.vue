<template>
  <div class="image-detection">
    <div class="content-box">
      <div class="header-section">
        <h2 class="title">📷 违规图像检测</h2>
        <p class="subtitle">可识别色情、政治、恐怖等违规图片</p>
      </div>

      <div class="upload-container">
        <div class="preview-container" v-if="previewImage">
          <img :src="previewImage" alt="Preview" class="preview-image">
          <button @click="clearPreview" class="close-button">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="upload-area" @dragover.prevent @drop="handleDrop"
             :class="{ 'has-preview': previewImage }">
          <div v-if="!previewImage" class="upload-icon">
            <i class="fas fa-cloud-upload-alt"></i>
          </div>
          <label class="custom-file-input">
            {{ previewImage ? '更换图片' : '选择或拖放图片到此处' }}
            <input type="file" @change="uploadImage" accept="image/*" />
          </label>
          <p v-if="!previewImage" class="file-requirements">
            支持 JPG/PNG 格式，最大 5MB
          </p>
        </div>
      </div>

      <div v-if="isLoading" class="loading-container">
        <div class="spinner"></div>
        <p>正在分析图片内容...</p>
      </div>

      <div v-if="result" class="result-section">
        <div class="result-header">
          <h3 class="result-title">检测结果</h3>
          <div class="detection-time">
            <i class="far fa-clock"></i> 检测耗时: {{ detectionTime }}秒
          </div>
        </div>

        <div class="result-card">
          <div :class="['result-icon', resultClass]">
            <i :class="iconClass"></i>
          </div>
          <div class="result-content">
            <p class="class-label">检测类别:</p>
            <h4 class="predicted-class">{{ result.predicted_class }}</h4>
            <p class="probability">置信度: {{ (result.probability * 100).toFixed(2) }}%</p>
          </div>
        </div>

        <div class="result-footer">
          <p v-if="result.predicted_class === 'neutral'" class="safe-message">
            <i class="fas fa-check-circle"></i> 该图片内容安全，未检测到违规内容
          </p>
          <p v-else class="warning-message">
            <i class="fas fa-exclamation-triangle"></i> 检测到疑似违规内容，请谨慎处理
          </p>
        </div>
      </div>

      <div v-if="!result && !previewImage && !isLoading" class="info-text">
        <div class="info-icon">
          <i class="fas fa-info-circle"></i>
        </div>
        <p>请上传需要检测的图片文件</p>
        <p class="subtext">系统将自动分析图片内容并给出安全评估</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      result: null,
      previewImage: null,
      isLoading: false,
      detectionTime: 0,
      startTime: 0
    };
  },
  computed: {
      resultClass() {
        // 当检测结果为 neutral 或 正常时，返回 normal（绿色）
        return (this.result?.predicted_class === 'neutral' || this.result?.predicted_class === '正常')
          ? 'normal'
          : 'abnormal';
      },
      iconClass() {
        // 当检测结果为 neutral 或 正常时，显示绿色勾号，否则显示警告图标
        return (this.result?.predicted_class === 'neutral' || this.result?.predicted_class === '正常')
          ? 'fas fa-check-circle'
          : 'fas fa-exclamation-triangle';
      }
    },
  methods: {
    async uploadImage(event) {
      const file = event.target.files[0];
      if (!file) return;
      this.processImage(file);
    },
    handleDrop(event) {
      event.preventDefault();
      const file = event.dataTransfer.files[0];
      if (file) {
        this.processImage(file);
      }
    },
    async processImage(file) {
      // 验证文件类型和大小
      if (!['image/jpeg', 'image/png'].includes(file.type)) {
        this.showError('请选择JPG或PNG格式的图片');
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        this.showError('文件大小不能超过5MB');
        return;
      }

      const reader = new FileReader();
      reader.onloadend = async (e) => {
        this.previewImage = e.target.result;
        const base64Image = e.target.result.split(',')[1];

        this.isLoading = true;
        this.startTime = new Date().getTime();

        try {
          const response = await axios.post('http://localhost:8080/detect_image', {
            image: base64Image
          });

          if (response.data.code === '00') {
            this.detectionTime = ((new Date().getTime() - this.startTime) / 1000).toFixed(2);
            this.result = {
              predicted_class: response.data.predicted_class,
              probability: response.data.probability
            };
          } else {
            this.showError('检测服务返回错误: ' + response.data.message);
          }
        } catch (error) {
          console.error('请求失败:', error);
          this.showError('网络请求失败，请重试');
        } finally {
          this.isLoading = false;
        }
      };
      reader.readAsDataURL(file);
    },
    clearPreview() {
      this.previewImage = null;
      this.result = null;
      this.detectionTime = 0;
    },
    showError(message) {
      this.result = {
        predicted_class: message,
        probability: 0
      };
      setTimeout(() => {
        this.result = null;
      }, 3000);
    }
  }
};
</script>

<style scoped>
.image-detection {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.content-box {
  background: white;
  padding: 30px 40px;
  border-radius: 16px;
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 600px;
  width: 100%;
  transition: all 0.3s ease;
}

.header-section {
  margin-bottom: 25px;
}

.title {
  font-size: 2.2rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 5px;
  background: linear-gradient(90deg, #3498db, #2c3e50);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  font-size: 1rem;
  color: #7f8c8d;
  margin-top: 0;
}

.upload-container {
  position: relative;
  margin: 30px 0;
}

.upload-area {
  border: 2px dashed #dfe6e9;
  border-radius: 12px;
  padding: 30px;
  transition: all 0.3s ease;
  cursor: pointer;
  background-color: #f8f9fa;
}

.upload-area:hover {
  border-color: #3498db;
  background-color: #f1f9ff;
}

.upload-area.has-preview {
  padding: 15px;
}

.upload-icon {
  font-size: 3rem;
  color: #bdc3c7;
  margin-bottom: 15px;
}

.preview-container {
  position: relative;
  width: 100%;
  max-width: 400px;
  height: 250px;
  margin: 0 auto 20px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.preview-image:hover {
  transform: scale(1.02);
}

.close-button {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  background: rgba(0, 0, 0, 0.8);
  transform: rotate(90deg);
}

.custom-file-input {
  display: inline-block;
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
  font-size: 1.1rem;
  font-weight: 500;
  padding: 12px 30px;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
  position: relative;
  margin-bottom: 10px;
}

.custom-file-input:hover {
  background: linear-gradient(135deg, #2980b9, #3498db);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4);
}

.custom-file-input input {
  position: absolute;
  left: 0;
  top: 0;
  opacity: 0;
  width: 100%;
  height: 100%;
  cursor: pointer;
}

.file-requirements {
  font-size: 0.9rem;
  color: #95a5a6;
  margin-top: 10px;
}

.loading-container {
  margin: 30px 0;
  padding: 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  margin: 0 auto 15px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.result-section {
  margin-top: 30px;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.result-title {
  font-size: 1.5rem;
  color: #2c3e50;
  margin: 0;
}

.detection-time {
  font-size: 0.9rem;
  color: #7f8c8d;
  background: #f1f3f4;
  padding: 5px 10px;
  border-radius: 15px;
}

.result-card {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 25px;
  padding: 25px;
  border-radius: 12px;
  background: #f8f9fa;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.result-icon {
  font-size: 3rem;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.normal {
  color: #27ae60;
  background: rgba(39, 174, 96, 0.1);
  box-shadow: 0 0 0 8px rgba(39, 174, 96, 0.1);
}

.abnormal {
  color: #e74c3c;
  background: rgba(231, 76, 60, 0.1);
  box-shadow: 0 0 0 8px rgba(231, 76, 60, 0.1);
}

.result-content {
  text-align: left;
  flex-grow: 1;
}

.class-label {
  color: #7f8c8d;
  font-size: 0.95rem;
  margin-bottom: 5px;
}

.predicted-class {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 5px 0;
}

.probability {
  color: #7f8c8d;
  font-size: 1.1rem;
  margin-top: 10px;
}

.result-footer {
  padding: 15px;
  border-radius: 8px;
}

.safe-message {
  color: #27ae60;
  background: rgba(39, 174, 96, 0.1);
  padding: 12px;
  border-radius: 8px;
  margin: 0;
}

.warning-message {
  color: #e74c3c;
  background: rgba(231, 76, 60, 0.1);
  padding: 12px;
  border-radius: 8px;
  margin: 0;
}

.info-text {
  padding: 20px;
  border-radius: 8px;
  background: #f8f9fa;
  margin-top: 20px;
}

.info-icon {
  font-size: 2rem;
  color: #3498db;
  margin-bottom: 10px;
}

.subtext {
  color: #95a5a6;
  font-size: 0.9rem;
  margin-top: 5px;
}

@media (max-width: 600px) {
  .content-box {
    padding: 20px;
  }

  .title {
    font-size: 1.8rem;
  }

  .result-card {
    flex-direction: column;
    text-align: center;
  }

  .result-content {
    text-align: center;
  }
}
</style>