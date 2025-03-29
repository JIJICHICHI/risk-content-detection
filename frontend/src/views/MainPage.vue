<template>
  <div class="main-page">
    <div class="background-glow"></div>
    <div class="content-box">
      <h1 class="title">✨基于大模型的风险内容检测系统</h1>
      <p class="description">请选择您需要的检测类型</p>

      <div class="options-grid">
        <router-link
          to="/text-detection"
          class="option-card text-card"
          @mouseenter="hoverEffect('text')"
          @mouseleave="resetHover"
          @mousemove="handleMouseMove"
        >
          <div class="card-icon">
            <i class="fa-solid fa-file-lines"></i>
          </div>
          <span>文本检测</span>
          <div class="hover-highlight"></div>
        </router-link>

        <router-link
          to="/image-detection"
          class="option-card image-card"
          @mouseenter="hoverEffect('image')"
          @mouseleave="resetHover"
          @mousemove="handleMouseMove"
        >
          <div class="card-icon">
            <i class="fa-solid fa-image"></i>
          </div>
          <span>图像检测</span>
          <div class="hover-highlight"></div>
        </router-link>

        <router-link
          to="/audio-detection"
          class="option-card audio-card"
          @mouseenter="hoverEffect('audio')"
          @mouseleave="resetHover"
          @mousemove="handleMouseMove"
        >
          <div class="card-icon">
            <i class="fa-solid fa-volume-high"></i>
          </div>
          <span>音频检测</span>
          <div class="hover-highlight"></div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      mouseX: 0,
      mouseY: 0
    };
  },
  methods: {
    hoverEffect(type) {
      // 添加动态效果逻辑
      const card = document.querySelector(`.${type}-card`);
      card.style.transform = 'scale(1.05)';
      card.style.boxShadow = '0 12px 30px rgba(0, 0, 0, 0.3)';
    },
    resetHover() {
      // 重置效果
      const cards = document.querySelectorAll('.option-card');
      cards.forEach(card => {
        card.style.transform = 'scale(1)';
        card.style.boxShadow = '0 8px 20px rgba(0, 0, 0, 0.2)';
      });
    },
    handleMouseMove(event) {
      const card = event.currentTarget;
      const rect = card.getBoundingClientRect();
      this.mouseX = event.clientX - rect.left;
      this.mouseY = event.clientY - rect.top;
      const highlight = card.querySelector('.hover-highlight');
      highlight.style.setProperty('--x', `${this.mouseX}px`);
      highlight.style.setProperty('--y', `${this.mouseY}px`);
    }
  }
};
</script>

<style scoped>
/* 引入 Font Awesome 图标库 */
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css');

.main-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(45deg, #0f0c29, #302b63, #24243e);
  position: relative;
  overflow: hidden;
}

.background-glow {
  position: absolute;
  width: 800px;
  height: 800px;
  background: radial-gradient(circle, rgba(92, 100, 255, 0.4) 0%, transparent 60%);
  animation: gradientFlow 10s infinite alternate;
  filter: blur(30px);
}

@keyframes gradientFlow {
  0% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.2;
  }
  100% {
    transform: translate(50%, 50%) scale(1.3);
    opacity: 0.6;
  }
}

.content-box {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border-radius: 30px;
  padding: 4rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
  z-index: 1;
  position: relative;
  width: 90%;
  max-width: 900px;
  text-align: center;
}

.title {
  font-size: 3rem;
  font-weight: 700;
  background: linear-gradient(45deg, #ffffff, #a2bfff);
  -webkit-background-clip: text;
  color: transparent;
  margin-bottom: 2rem;
  letter-spacing: 2px;
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
}

.description {
  font-size: 1.3rem;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 3rem;
  font-weight: 300;
}

.options-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 2rem;
}

.option-card {
  position: relative;
  padding: 2.5rem;
  border-radius: 20px;
  text-decoration: none;
  color: white;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 220px;
}

.option-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.1);
  border-radius: inherit;
  z-index: -1;
  transform: scale(0.9);
  transition: transform 0.3s ease;
}

.option-card:hover::before {
  transform: scale(1);
}

.card-icon {
  width: 80px;
  height: 80px;
  margin-bottom: 2rem;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  display: grid;
  place-items: center;
  transition: transform 0.3s ease;
  font-size: 2rem;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
}

.option-card:hover .card-icon {
  transform: translateY(-10px) rotate(5deg);
}

.hover-highlight {
  position: absolute;
  background: radial-gradient(300px circle at var(--x) var(--y), rgba(255, 255, 255, 0.25), transparent);
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
}

.option-card:hover .hover-highlight {
  opacity: 1;
}

/* 不同卡片颜色方案 */
.image-card {
  background: linear-gradient(45deg, #6366f1, #8b5cf6);
}

.audio-card {
  background: linear-gradient(45deg, #3b82f6, #60a5fa);
}

.text-card {
  background: linear-gradient(45deg, #10b981, #34d399);
}

.option-card span {
  font-size: 1.2rem;
  font-weight: 500;
  text-shadow: 0 0 5px rgba(0, 0, 0, 0.3);
}

@media (max-width: 768px) {
  .content-box {
    padding: 2.5rem;
    margin: 1.5rem;
  }

  .title {
    font-size: 2.2rem;
  }

  .description {
    font-size: 1.1rem;
  }
}
</style>