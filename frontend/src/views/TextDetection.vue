<template>
  <div class="container">
    <div class="header">
      <h1 class="title">诈骗文本检测系统</h1>
      <p class="subtitle">输入可疑文本，获取分析结果</p>
    </div>

    <div class="input-section">
      <textarea
        v-model="inputText"
        placeholder="请输入需要检测的文本内容..."
        class="input-box"
        rows="5"
      ></textarea>
      <button
        @click="analyzeText"
        :disabled="loading"
        class="analyze-btn"
      >
        <span v-if="!loading">开始检测</span>
        <span v-else class="spinner"></span>
      </button>
    </div>

    <div class="results-container">
      <div v-if="bertResult" class="result-card">
        <div class="card-header">
          <h2><i class="icon fas fa-robot"></i> ROBERTA 诈骗分类</h2>
        </div>
        <div class="card-body">
          <div class="result-item">
            <span class="label">分类结果:</span>
            <span :class="['value', bertResult.category === '诈骗' ? 'fraud' : 'legit']">
              {{ bertResult.category }}
            </span>
          </div>
          <div class="result-item">
            <span class="label">分析耗时:</span>
            <span class="value">{{ bertResult.timeTaken }} 秒</span>
          </div>
        </div>
      </div>

      <div v-if="deepseekResponse.length > 0" class="result-card">
        <div class="card-header">
          <h2><i class="icon fas fa-brain"></i> DeepSeek 智能分析</h2>
        </div>
        <div class="card-body">
          <div class="analysis-text" v-html="formattedDeepSeekResponse"></div>
          <div v-if="deepseekComplete" class="result-item time-info">
            <span class="label">总分析耗时:</span>
            <span class="value">{{ deepseekTime }} 秒</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      inputText: "",
      bertResult: null,
      deepseekResponse: [],
      deepseekComplete: false,
      deepseekTime: 0,
      loading: false,
    };
  },
  computed: {
    formattedDeepSeekResponse() {
      return this.deepseekResponse.join('\n')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
    }
  },
  methods: {
    async analyzeText() {
      if (!this.inputText.trim()) {
        this.$toast.error("请输入需要检测的文本内容！");
        return;
      }
      this.bertResult = null;
      this.deepseekResponse = [];
      this.deepseekComplete = false;
      this.loading = true;

      const startDeepSeek = () => {
        const startTime = Date.now();
        fetch("http://localhost:5000/text_fraud_deepseek", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: this.inputText })
        }).then(response => {
          const reader = response.body.getReader();
          const decoder = new TextDecoder("utf-8");
          let accumulatedText = "";
          const readStream = async () => {
            while (true) {
              const { value, done } = await reader.read();
              if (done) break;
              const lines = decoder.decode(value).trim().split("\n");
              lines.forEach(line => {
                try {
                  const json = JSON.parse(line);
                  accumulatedText = json.deepseek_analysis;
                  this.deepseekResponse = accumulatedText.split("\n");
                  if (json.complete) {
                    this.deepseekComplete = true;
                    this.deepseekTime = (Date.now() - startTime) / 1000;
                    this.loading = false;
                  }
                } catch (e) {
                  console.error("解析错误", e, line);
                }
              });
            }
          };
          readStream();
        }).catch(error => {
          console.error("DeepSeek 请求错误", error);
          this.loading = false;
        });
      };

      const startTime = Date.now();
      fetch("http://localhost:5000/text_fraud_bert", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: this.inputText })
      }).then(response => response.json())
        .then(data => {
          this.bertResult = {
            category: data.bert_category,
            timeTaken: data.time_taken.toFixed(2)
          };
          startDeepSeek();
        }).catch(error => {
          console.error("BERT 请求错误", error);
          this.loading = false;
        });
    }
  }
};
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');

:root {
  --primary-color: #4361ee;
  --secondary-color: #3f37c9;
  --success-color: #4cc9f0;
  --danger-color: #f72585;
  --warning-color: #f8961e;
  --light-color: #f8f9fa;
  --dark-color: #212529;
  --gray-color: #6c757d;
  --border-radius: 8px;
  --box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  --transition: all 0.3s ease;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Noto Sans SC', sans-serif;
  background-color: #f5f7fa;
  color: var(--dark-color);
  line-height: 1.6;
}

.container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 0 1rem;
}

.header {
  text-align: center;
  margin-bottom: 2rem;
}

.title {
  font-size: 2.2rem;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: 1rem;
  color: var(--gray-color);
}

.input-section {
  background: white;
  padding: 1.5rem;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  margin-bottom: 2rem;
}

.input-box {
  width: 100%;
  padding: 1rem;
  font-size: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: var(--border-radius);
  resize: none;
  transition: var(--transition);
  margin-bottom: 1rem;
}

.input-box:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(67, 97, 238, 0.2);
}

.analyze-btn {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  font-size: 1rem;
  font-weight: 500;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: var(--transition);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
}

.analyze-btn:hover {
  background-color: var(--secondary-color);
  transform: translateY(-1px);
}

.analyze-btn:disabled {
  background-color: var(--gray-color);
  cursor: not-allowed;
  transform: none;
}

.spinner {
  display: inline-block;
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

.results-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

.result-card {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  overflow: hidden;
}

.card-header {
  background-color: var(--primary-color);
  color: white;
  padding: 1rem 1.5rem;
}

.card-header h2 {
  font-size: 1.2rem;
  font-weight: 500;
  display: flex;
  align-items: center;
}

.icon {
  margin-right: 0.5rem;
}

.card-body {
  padding: 1.5rem;
}

.result-item {
  display: flex;
  margin-bottom: 0.8rem;
}

.result-item:last-child {
  margin-bottom: 0;
}

.label {
  font-weight: 500;
  color: var(--gray-color);
  min-width: 100px;
}

.value {
  color: var(--dark-color);
}

.value.fraud {
  color: var(--danger-color);
  font-weight: 700;
}

.value.legit {
  color: #2ecc71;
  font-weight: 700;
}

.analysis-text {
  line-height: 1.8;
  margin-bottom: 1rem;
}

.analysis-text strong {
  color: var(--primary-color);
}

.time-info {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

@media (min-width: 768px) {
  .results-container {
    grid-template-columns: 1fr 1fr;
  }

  .analyze-btn {
    width: auto;
  }
}
.results-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
</style>