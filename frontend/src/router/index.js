import { createRouter, createWebHistory } from 'vue-router';
import MainPage from '../views/MainPage.vue';  // 引入主界面组件
import ImageDetection from '../views/ImageDetection.vue';
import AudioDetection from '../views/AudioDetection.vue';
import TextDetection from '../views/TextDetection.vue';
import WelcomePage from '../views/WelcomePage.vue'; // 引入欢迎界面组件

const routes = [
  { path: '/', component: WelcomePage }, // 默认显示欢迎界面
  { path: '/main', component: MainPage }, // 主界面路径
  { path: '/image-detection', component: ImageDetection },
  { path: '/audio-detection', component: AudioDetection },
  { path: '/text-detection', component: TextDetection }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;