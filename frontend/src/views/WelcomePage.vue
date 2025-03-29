<template>
  <div class="welcome-page">
    <!-- 背景动画元素 -->
    <div class="bg-animations">
      <span class="circle circle-1"></span>
      <span class="circle circle-2"></span>
      <span class="circle circle-3"></span>
    </div>
    <div class="content">
      <h1 class="welcome-title">欢迎使用基于大模型的风险内容检测系统</h1>
      <router-link to="/main" class="start-button">开始使用</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WelcomePage'
};
</script>

<style scoped>
/* 全局字体 */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

.welcome-page {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(45deg, #0f0c29, #302b63, #24243e);
  color: white;
  font-family: 'Poppins', sans-serif;
  position: relative;
  overflow: hidden;
}

/* 背景动画元素样式 */
.bg-animations {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.circle {
  position: absolute;
  border-radius: 50%;
  animation: float 6s ease-in-out infinite;
}

.circle-1 {
  width: 100px;
  height: 100px;
  background: rgba(255, 255, 255, 0.1);
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.circle-2 {
  width: 150px;
  height: 150px;
  background: rgba(255, 255, 255, 0.1);
  top: 30%;
  right: 15%;
  animation-delay: 1s;
}

.circle-3 {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.1);
  bottom: 20%;
  left: 20%;
  animation-delay: 2s;
}

@keyframes float {
  0% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
  100% {
    transform: translateY(0px);
  }
}

/* 内容区域样式 */
.content {
  text-align: center;
  z-index: 1;
  animation: fadeIn 1s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.welcome-title {
  font-size: 3.5rem;
  margin-bottom: 4rem;
  font-weight: 600;
  text-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
}


.start-button {
  padding: 1.2rem 2.5rem;
  background-color: #10b981;
  color: white;
  text-decoration: none;
  border-radius: 50px;
  font-size: 1.3rem;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.start-button:hover {
  background-color: #0ea070;
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
}
</style>