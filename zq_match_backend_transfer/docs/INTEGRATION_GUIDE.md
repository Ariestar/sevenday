# 前后端联调集成指南

面向前端的快速对接说明，帮助在不改动当前后端逻辑的前提下快速集成与调试。

## 一、环境与文档
- 健康检查：GET `/health/` → `{ "status": "ok" }`
- 服务元信息：GET `/meta/` → `{ service, env }`
- OpenAPI 文档：
  - JSON：GET `/docs/schema/`
  - Swagger UI：GET `/docs/`
  - ReDoc：GET `/docs/redoc/`
  - 可直接导入 Postman 或用于生成前端 SDK（如 openapi-typescript）

## 二、认证
- 使用 JWT（Bearer Token）
- 登录接口（示例，按项目实际登录接口为准）：`POST /oauth/token/` 或微信/QQ 登录接口
- 所有需要鉴权的接口在 Header 中携带：
  - `Authorization: Bearer <access_token>`

## 三、通用返回格式
后端已启用自定义渲染器，统一返回结构：
```json
{
  "code": 0,
  "msg": "success",
  "data": { ... },
  "errors": null
}
```
- 列表分页（以 DRF 分页为基础）：
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "count": 123,
    "next": "?page=3",
    "previous": "?page=1",
    "results": [ ... ]
  }
}
```
- 标准错误（已集成 drf_standardized_errors）：
```json
{
  "code": 400,
  "msg": "参数校验失败",
  "errors": { "field": ["错误信息"] },
  "data": null
}
```

## 四、常用端点速览
- 报名表
  - GET `/applications/my-application/` 获取我的报名表
  - POST `/applications/` 创建报名表
  - POST `/applications/self-match/` 自助匹配（每日限次）
  - GET `/applications/self-match/status` 查询今日次数与匹配状态
  - GET `/applications/match-status/` 查询是否已匹配与队友
- 队伍
  - GET `/teams/` 列表（分页/筛选/排序）
- 任务/打卡
  - GET `/tasks/` 列表
  - POST `/posts/` 创建打卡（需图片、任务有效期内、同队伍同任务仅一次）
  - GET `/posts/my-posts/` 我的队伍打卡

更多端点见 `/docs/`。

## 五、前端示例（伪代码）
```ts
// axios base
const api = axios.create({ baseURL: process.env.API_BASE_URL });
api.interceptors.request.use((cfg) => {
  const token = localStorage.getItem('access_token');
  if (token) cfg.headers.Authorization = `Bearer ${token}`;
  return cfg;
});

// 自助匹配
await api.post('/applications/self-match/');

// 我的打卡
const { data } = await api.get('/posts/my-posts/', { params: { page: 1, page_size: 10 } });
const list = data.data.results;
```

## 六、联调建议
- 开发环境已放开 CORS（允许 `Authorization`）
- 建议使用 `/docs/` 直接调试与查看参数说明
- 若需 Mock，可将 `/docs/schema/` 导入到 swagger-mock 工具生成假数据

## 七、常见问题
- 401/403：检查是否携带了 `Authorization: Bearer <token>`
- 429（自助匹配）：达到每日次数限制
- 图片上传：表单 `multipart/form-data`，字段名 `photo`，大小 ≤ 5MB，类型 jpg/png/webp

若需要补充更多示例或生成类型定义（TypeScript），请告诉我你的前端技术栈（React/Vue/UniApp 等），我可以直接产出可用模板。