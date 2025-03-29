<template>
  <div class="audio-detection-container">
    <div class="header-section">
      <h1 class="main-title">
        <i class="fas fa-microphone-alt"></i> 音频真伪检测&诈骗分析
      </h1>
      <p class="subtitle">基于深度学习的音频伪造检测与诈骗分析解决方案</p>
    </div>

    <div class="upload-section card">
      <div class="upload-header">
        <h2><i class="fas fa-cloud-upload-alt"></i> 上传音频文件</h2>
        <p class="upload-hint">支持 WAV/MP3 格式，最大20MB</p>
      </div>

      <div class="upload-content">
        <div class="file-input-wrapper">
          <label class="file-upload-label">
            <input type="file" @change="handleFileUpload" accept="audio/*" />
            <div class="upload-box" :class="{'has-file': selectedFile}">
              <i class="fas fa-file-audio" :class="{'pulse': loading}"></i>
              <span v-if="!selectedFile" class="upload-text">点击或拖拽文件到此处</span>
              <span v-else class="file-name">{{ selectedFile.name }}</span>
              <span v-if="selectedFile" class="file-size">{{ formatFileSize(selectedFile.size) }}</span>
            </div>
          </label>
        </div>

        <div class="preview-section" v-if="audioPreview">
          <div class="audio-player">
            <audio controls :src="audioPreview" :autoplay="false"></audio>
            <button @click="clearFile" class="clear-btn">
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>

        <button
          @click="submitFile"
          :disabled="!selectedFile || loading"
          class="analyze-btn"
          :class="{'loading': loading}"
        >
          <span v-if="loading" class="spinner"></span>
          <span v-else>开始分析 <i class="fas fa-search"></i></span>
        </button>
      </div>
    </div>

    <div v-if="error" class="error-card card">
      <div class="error-content">
        <i class="fas fa-exclamation-circle"></i>
        <div class="error-details">
          <h3>分析出错</h3>
          <p>{{ error }}</p>
        </div>
      </div>
    </div>

    <div v-if="results.length" class="results-section">
      <div class="summary-card card">
        <div class="summary-header">
          <h2><i class="fas fa-chart-pie"></i> 检测概览</h2>
        </div>
        <div class="summary-content">
          <div class="verdict">
            <div class="verdict-icon" :class="{'fake': overallResult === '深度伪造音频'}">
              <i :class="overallResult === '深度伪造音频' ? 'fas fa-exclamation-triangle' : 'fas fa-check-circle'"></i>
            </div>
            <div class="verdict-details">
              <h3>检测结果</h3>
              <p class="verdict-text" :class="{'fake': overallResult === '深度伪造音频'}">
                {{ overallResult }}
              </p>
              <div class="confidence-meter">
                <div class="meter-labels">
                  <span>可信度</span>
                  <span>{{ overallConfidence.toFixed(2) }}%</span>
                </div>
                <div class="meter-bar">
                  <div
                    class="meter-fill"
                    :class="{'high-risk': overallConfidence > 50}"
                    :style="{width: `${overallConfidence}%`}"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="chart-card card">
        <div class="chart-header">
          <h2><i class="fas fa-chart-line"></i> 分段分析</h2>
          <div class="chart-legend">
            <div class="legend-item">
              <span class="legend-color real"></span>
              <span>真实音频</span>
            </div>
            <div class="legend-item">
              <span class="legend-color fake"></span>
              <span>伪造音频</span>
            </div>
          </div>
        </div>
        <div class="chart-container">
          <canvas ref="chartCanvas"></canvas>
        </div>
      </div>

      <div v-if="transcribedText" class="transcription-card card">
        <div class="transcription-header">
          <h2><i class="fas fa-align-left"></i> 转录文本</h2>
          <button @click="copyText" class="copy-btn">
            <i class="far fa-copy"></i> 复制
          </button>
        </div>
        <div class="transcription-content">
          <p>{{ transcribedText }}</p>
        </div>
      </div>

      <div v-if="fraudAnalysis" class="analysis-card card">
        <div class="analysis-header">
          <h2><i class="fas fa-shield-alt"></i> ROBERTA分类结果</h2>
          <div class="risk-badge" :class="fraudAnalysis.bertCategory === '正常文本' ? 'low' : 'high'">
            {{ fraudAnalysis.bertCategory }}
          </div>
        </div>
        <div class="analysis-content">
          <div class="ai-analysis">
            <div class="ai-header">
              <i class="fas fa-robot"></i>
              <h3>deepseek分析报告</h3>
            </div>
            <div class="ai-text" v-html="fraudAnalysis.deepseekAnalysis"></div>
          </div>
          <div class="warning-tips" v-if="fraudAnalysis.bertCategory !== '正常文本'">
            <h3><i class="fas fa-exclamation-triangle"></i> 安全建议</h3>
            <ul>
              <li>不要轻信音频中的任何财务要求</li>
              <li>通过其他渠道验证对方身份</li>
              <li>不要透露个人敏感信息</li>
              <li>如已受骗，请立即报警</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { Chart, registerables } from 'chart.js';

export default {
  data() {
    return {
      selectedFile: null,
      audioPreview: null,
      results: [],
      loading: false,
      error: null,
      chart: null,
      fraudAnalysis: null,
      transcribedText: null,
      chartData: {
        labels: [],
        datasets: [
          {
            label: '伪造概率',
            data: [],
            backgroundColor: (context) => {
              const value = context.raw;
              return value > 0.5
                ? 'rgba(255, 99, 132, 0.7)'
                : 'rgba(54, 162, 235, 0.7)';
            },
            borderColor: (context) => {
              const value = context.raw;
              return value > 0.5
                ? 'rgba(255, 99, 132, 1)'
                : 'rgba(54, 162, 235, 1)';
            },
            borderWidth: 1,
            borderRadius: 4,
            borderSkipped: false,
          }
        ]
      },
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            max: 1,
            ticks: {
              stepSize: 0.2,
              callback: (value) => `${value * 100}%`
            },
            grid: {
              color: 'rgba(0, 0, 0, 0.05)'
            }
          },
          x: {
            grid: {
              display: false
            }
          }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (context) => {
                return `伪造概率: ${(context.raw * 100).toFixed(2)}%`;
              }
            }
          },
          annotation: {
            annotations: {
              thresholdLine: {
                type: 'line',
                yMin: 0.5,
                yMax: 0.5,
                borderColor: 'rgba(255, 99, 132, 0.5)',
                borderWidth: 2,
                borderDash: [6, 6],
              }
            }
          }
        },
        animation: {
          duration: 1000,
          easing: 'easeOutQuart'
        }
      }
    };
  },
  computed: {
    overallResult() {
      return this.overallConfidence > 50 ? '深度伪造音频' : '真实音频';
    },
    overallConfidence() {
      if (!this.results.length) return 0;
      const avg = this.results.reduce((acc, curr) => acc + curr.confidence, 0) / this.results.length;
      return avg * 100;
    }
  },
  mounted() {
    Chart.register(...registerables);
  },
  methods: {
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (!file) return;

      const allowedTypes = ['audio/wav', 'audio/mpeg', 'audio/x-wav'];
      if (!allowedTypes.includes(file.type)) {
        this.error = '请选择WAV或MP3格式的音频文件';
        return;
      }

      const maxSize = 20 * 1024 * 1024;
      if (file.size > maxSize) {
        this.error = '文件大小超过20MB，请选择较小的文件';
        return;
      }

      this.selectedFile = file;
      this.error = null;
      this.results = [];
      this.fraudAnalysis = null;

      const reader = new FileReader();
      reader.onload = (e) => {
        this.audioPreview = e.target.result;
      };
      reader.readAsDataURL(file);

      if (this.chart) {
        this.chart.destroy();
        this.chart = null;
      }
    },
    clearFile() {
      this.selectedFile = null;
      this.audioPreview = null;
      this.results = [];
      this.fraudAnalysis = null;
      if (this.chart) {
        this.chart.destroy();
        this.chart = null;
      }
    },
    async submitFile() {
      if (!this.selectedFile) {
        this.error = '请先选择要检测的音频文件';
        return;
      }

      this.loading = true;
      this.error = null;

      try {
        const formData = new FormData();
        formData.append('file', this.selectedFile);
        formData.append('audio', this.selectedFile);

        const [fraudResponse, detectionResponse] = await Promise.all([
          axios.post('http://localhost:5000/audio_fraud_analysis', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          }),
          axios.post('http://localhost:5001/detect', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          })
        ]);

        this.fraudAnalysis = {
          bertCategory: fraudResponse.data.bert_category,
          deepseekAnalysis: fraudResponse.data.deepseek_analysis
        };
        this.transcribedText = fraudResponse.data.transcribed_text;

        this.results = detectionResponse.data.results.map(segment => ({
          ...segment,
          confidence: parseFloat(segment.confidence)
        }));

        this.prepareChartData();
        this.renderChart();

      } catch (error) {
        console.error('检测失败:', error);
        this.error = error.response?.data?.error || '分析过程中出现错误，请稍后再试';
      } finally {
        this.loading = false;
      }
    },
    prepareChartData() {
      const timePoints = this.results.map((segment, index) =>
        `分段 ${index + 1} (${segment.start.toFixed(2)}s-${segment.end.toFixed(2)}s)`
      );

      this.chartData.labels = timePoints;
      this.chartData.datasets[0].data = this.results.map(s => s.confidence);
    },
    renderChart() {
      if (this.chart) {
        this.chart.destroy();
      }

      this.$nextTick(() => {
        const ctx = this.$refs.chartCanvas;
        if (!ctx) return;

        this.chart = new Chart(ctx, {
          type: 'bar',
          data: this.chartData,
          options: this.chartOptions
        });
      });
    },
    copyText() {
      navigator.clipboard.writeText(this.transcribedText)
        .then(() => {
          this.$toast.success('文本已复制到剪贴板');
        })
        .catch(err => {
          console.error('复制失败:', err);
          this.$toast.error('复制失败');
        });
    }
  },
  beforeUnmount() {
    if (this.chart) {
      this.chart.destroy();
    }
  }
};
</script>

<style scoped>
:root {
  --primary-color: #4361ee;
  --primary-light: #eef2ff;
  --secondary-color: #3f37c9;
  --success-color: #4cc9f0;
  --danger-color: #f72585;
  --warning-color: #f8961e;
  --text-color: #2b2d42;
  --text-light: #8d99ae;
  --bg-color: #f8f9fa;
  --card-bg: #ffffff;
  --border-radius: 12px;
  --box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  --transition: all 0.3s ease;
}

.audio-detection-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
  color: var(--text-color);
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
}

.header-section {
  text-align: center;
  margin-bottom: 2.5rem;
}

.main-title {
  font-size: 2.2rem;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}

.main-title i {
  font-size: 1.8rem;
}

.subtitle {
  font-size: 1.1rem;
  color: var(--text-light);
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

.card {
  background: var(--card-bg);
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  transition: var(--transition);
}

.card:hover {
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.12);
}

.upload-section {
  border-top: 4px solid var(--primary-color);
}

.upload-header {
  margin-bottom: 1.5rem;
}

.upload-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-color);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.upload-hint {
  color: var(--text-light);
  font-size: 0.9rem;
}

.upload-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.file-input-wrapper {
  width: 100%;
}

.file-upload-label {
  display: block;
  cursor: pointer;
}

.file-upload-label input {
  display: none;
}

.upload-box {
  border: 2px dashed #d1d5db;
  border-radius: var(--border-radius);
  padding: 2.5rem 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  transition: var(--transition);
  background-color: var(--primary-light);
}

.upload-box.has-file {
  border-color: var(--primary-color);
  background-color: rgba(67, 97, 238, 0.05);
}

.upload-box i {
  font-size: 2.5rem;
  color: var(--primary-color);
}

.upload-box:hover {
  border-color: var(--primary-color);
}

.upload-text {
  font-size: 1.1rem;
  color: var(--text-light);
}

.file-name {
  font-weight: 500;
  font-size: 1.1rem;
  color: var(--text-color);
  text-align: center;
  word-break: break-all;
}

.file-size {
  font-size: 0.9rem;
  color: var(--text-light);
}

.pulse {
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

.preview-section {
  width: 100%;
}

.audio-player {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.audio-player audio {
  flex: 1;
  max-width: calc(100% - 50px);
  height: 40px;
}

.clear-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #f1f5f9;
  border: none;
  color: var(--text-light);
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
}

.clear-btn:hover {
  background: #e2e8f0;
  color: var(--danger-color);
}

.analyze-btn {
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 50px;
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  margin: 0 auto;
  width: fit-content;
}

.analyze-btn:hover:not(:disabled) {
  background: var(--secondary-color);
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(67, 97, 238, 0.2);
}

.analyze-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.analyze-btn.loading {
  background: var(--primary-color);
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-card {
  border-left: 4px solid var(--danger-color);
  background-color: #fff5f7;
}

.error-content {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.error-content i {
  font-size: 1.5rem;
  color: var(--danger-color);
  margin-top: 0.25rem;
}

.error-details h3 {
  font-size: 1.2rem;
  color: var(--danger-color);
  margin-bottom: 0.5rem;
}

.error-details p {
  color: var(--text-color);
  line-height: 1.6;
}

.results-section {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

.summary-card {
  border-top: 4px solid var(--primary-color);
}

.summary-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.summary-content {
  display: flex;
  justify-content: center;
}

.verdict {
  display: flex;
  align-items: center;
  gap: 2rem;
  max-width: 600px;
  width: 100%;
}

.verdict-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(76, 201, 240, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.verdict-icon i {
  font-size: 2.5rem;
  color: var(--success-color);
}

.verdict-icon.fake {
  background: rgba(247, 37, 133, 0.1);
}

.verdict-icon.fake i {
  color: var(--danger-color);
}

.verdict-details {
  flex: 1;
}

.verdict-details h3 {
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-light);
  margin-bottom: 0.5rem;
}

.verdict-text {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--success-color);
  margin-bottom: 1rem;
}

.verdict-text.fake {
  color: var(--danger-color);
}

.confidence-meter {
  width: 100%;
}

.meter-labels {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: var(--text-light);
}

.meter-bar {
  height: 10px;
  background: #e9ecef;
  border-radius: 5px;
  overflow: hidden;
}

.meter-fill {
  height: 100%;
  background: var(--success-color);
  border-radius: 5px;
  transition: width 1s ease;
}

.meter-fill.high-risk {
  background: var(--danger-color);
}

.chart-card {
  border-top: 4px solid var(--primary-color);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.chart-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.chart-legend {
  display: flex;
  gap: 1.5rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

.legend-color.real {
  background: var(--success-color);
}

.legend-color.fake {
  background: var(--danger-color);
}

.chart-container {
  height: 400px;
  position: relative;
}

.transcription-card {
  border-top: 4px solid #6c757d;
}

.transcription-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.transcription-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.copy-btn {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  color: var(--text-light);
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.copy-btn:hover {
  background: #e9ecef;
  color: var(--text-color);
}

.transcription-content {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
}

.transcription-content p {
  line-height: 1.8;
  white-space: pre-wrap;
}

.analysis-card {
  border-top: 4px solid var(--warning-color);
}

.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.analysis-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.risk-badge {
  padding: 0.5rem 1rem;
  border-radius: 50px;
  font-weight: 600;
  font-size: 0.9rem;
}

.risk-badge.low {
  background: rgba(76, 201, 240, 0.1);
  color: var(--success-color);
}

.risk-badge.high {
  background: rgba(247, 37, 133, 0.1);
  color: var(--danger-color);
}

.analysis-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

.ai-analysis {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
}

.ai-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.ai-header h3 {
  font-size: 1.2rem;
  font-weight: 600;
}

.ai-header i {
  font-size: 1.5rem;
  color: var(--primary-color);
}

.ai-text {
  line-height: 1.8;
}

.ai-text >>> strong {
  color: var(--primary-color);
}

.warning-tips {
  background: #fff8e6;
  border-left: 4px solid var(--warning-color);
  border-radius: 0 8px 8px 0;
  padding: 1.5rem;
}

.warning-tips h3 {
  font-size: 1.2rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  color: var(--warning-color);
}

.warning-tips ul {
  padding-left: 1.5rem;
  line-height: 1.8;
}

.warning-tips li {
  margin-bottom: 0.5rem;
}

.info-section {
  border-top: 4px solid #6c757d;
  margin-top: 2rem;
}

.info-section h2 {
  font-size: 1.5rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.info-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  transition: var(--transition);
}

.info-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.05);
}

.info-item i {
  font-size: 2rem;
  color: var(--primary-color);
  margin-bottom: 1rem;
}

.info-item h3 {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.info-item p {
  color: var(--text-light);
  line-height: 1.6;
}

@media (max-width: 768px) {
  .main-title {
    font-size: 1.8rem;
  }

  .verdict {
    flex-direction: column;
    gap: 1.5rem;
    text-align: center;
  }

  .chart-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .analysis-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .chart-container {
    height: 300px;
  }
}

@media (max-width: 480px) {
  .audio-detection-container {
    padding: 1rem 0.5rem;
  }

  .main-title {
    font-size: 1.5rem;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>

<!-- 在index.html头部添加 -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.3.0/dist/chart.umd.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">