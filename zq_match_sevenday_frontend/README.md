# 专交遇见你 - 前端项目

「专交遇见你」是面向武汉大学在读学生的活动类小程序，核心业务包括：报名 → 匹配/组队 → 10 天打卡 → 广场展示 → 工作人员审核计分。

## 技术栈

- **框架**: uni-app (Vue 3)
- **构建工具**: Vite
- **目标平台**: 微信小程序

## 环境要求

- Node.js >= 14.0.0
- npm >= 6.0.0 或 pnpm >= 7.0.0
- 微信开发者工具

## 安装依赖

在项目根目录下执行：

```bash
npm install
```

或使用 pnpm：

```bash
pnpm install
```

## 编译运行

### 开发模式

1. 执行编译命令：

```bash
npm run dev
```

或使用 pnpm：

```bash
pnpm dev
```

2. 编译完成后，会在 `dist/dev/mp-weixin` 目录下生成微信小程序代码

3. 打开微信开发者工具：
   - 选择"导入项目"
   - 项目目录选择：`dist/dev/mp-weixin`
   - AppID 填写：在 `src/manifest.json` 中配置的 `mp-weixin.appid`
   - 点击"导入"

4. 在微信开发者工具中即可预览和调试小程序

### 生产模式

执行生产构建：

```bash
npm run build
```

或使用 pnpm：

```bash
pnpm build
```

编译完成后，会在 `dist/build/mp-weixin` 目录下生成生产代码，可直接上传到微信公众平台。

## 常用命令

- `npm run dev` - 开发模式编译到 `dist/dev/mp-weixin`
- `npm run build` - 生产模式编译到 `dist/build/mp-weixin`
- `npm run lint` - 检查代码是否符合规范
- `npm run lint --fix` - 检查代码并自动修复
- `npm run update:uni` - 使用 `uvm` 自动更新本地 uni-app 编译器版本

## 项目结构

```
match_zq_frontend/
├── src/                    # 源代码目录
│   ├── components/         # 可复用组件
│   ├── pages/             # 页面文件
│   ├── services/          # API 服务层
│   ├── static/            # 静态资源
│   ├── utils/             # 工具函数
│   ├── App.vue            # 应用入口
│   ├── main.js            # 入口文件
│   ├── manifest.json      # 应用配置
│   └── pages.json         # 页面路由配置
├── dist/                  # 编译输出目录（不提交到 Git）
│   ├── dev/               # 开发模式输出
│   └── build/             # 生产模式输出
├── package.json           # 项目依赖配置
└── vite.config.js         # Vite 构建配置
```

## 注意事项

1. **首次运行**：确保已安装所有依赖，编译命令会生成 `dist/dev/mp-weixin` 目录
2. **AppID 配置**：在 `src/manifest.json` 中配置正确的微信小程序 AppID
3. **API 配置**：后端 API 地址在 `src/utils/request.js` 中配置，开发阶段可使用本地模拟数据
4. **代码规范**：项目使用 ESLint 进行代码检查，提交前建议运行 `npm run lint`

## 开发说明

- 所有接口统一使用 `/api` 前缀
- 页面路由配置在 `src/pages.json` 中
- 组件统一放在 `src/components/` 目录
- 静态资源放在 `src/static/` 目录
- 业务常量统一在 `src/utils/constants.js` 中定义

## License

Copyright © ZiqiangStudio
