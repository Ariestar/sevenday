/**
 * 路由配置文件
 * 用于解决微信小程序代码依赖分析问题
 * 通过静态引用确保所有页面都能被正确识别
 * 
 * 注意：这个文件中的引用用于让微信小程序的代码依赖分析工具
 * 识别那些只通过 uni.navigateTo 动态引用的页面
 */

// 静态引用 team-name 页面，确保代码依赖分析工具能识别
// 使用注释方式引用，避免实际执行但能让依赖分析工具识别
// @ts-ignore
// eslint-disable-next-line
import '../pages/team-name/index.vue'

// 导出路由映射（用于类型检查和文档）
export const routeMap = {
  'team-name': '/pages/team-name/index'
}

// 这个文件会被 main.js 引用，确保依赖分析工具能识别所有页面
