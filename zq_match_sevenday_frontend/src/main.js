import { createSSRApp } from 'vue';
import App from './App.vue';
// 引入路由配置，确保所有页面都能被代码依赖分析工具识别
import './utils/routes.js';

export function createApp() {
  const app = createSSRApp(App);
  return {
    app,
  };
}
