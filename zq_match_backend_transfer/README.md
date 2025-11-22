# ZQ Match Backend

武汉大学自强匹配系统后端 API

## 📖 项目简介

ZQ Match Backend 是一个基于 Django + DRF 的匹配系统，用于帮助学生找到合适的学习伙伴。系统支持：

- 🎓 基于院系偏好的双向匹配算法
- 👥 队伍管理和协作
- ✅ 任务打卡和积分系统
- 📱 完整的 RESTful API

## ✨ 主要功能

### 用户系统
- 武汉大学邮箱注册/登录
- JWT Token 认证
- 个人资料管理
- 头像上传
- 密码修改
- QQ 绑定

### 匹配系统
- 提交报名表（院系偏好、性别偏好）
- 智能匹配算法
- 匹配状态查询
- 历史匹配记录

### 队伍系统
- 自动组队
- 队伍信息管理
- 队伍排行榜
- 解散队伍

### 任务系统
- 任务发布（管理员）
- 任务列表查看
- 进行中/即将开始的任务
- 任务打卡提交
- 积分累计

### 打卡系统
- 上传打卡照片
- 打卡记录查看
- 按任务筛选打卡

## 🚀 快速开始

### 环境要求
- Python 3.11+
- MySQL 8.0+ / SQLite 3
- Redis (生产环境)

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd zq_match_backend
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
# 开发环境
export DATABASE_URL='sqlite:///db.sqlite3'
export DJANGO_ENV='development'
export DJANGO_DEBUG='True'
```

4. **数据库迁移**
```bash
python manage.py migrate
```

5. **导入学院数据**
```bash
python manage.py import_academies
```

6. **创建管理员**
```bash
# 开发环境
export LOCAL_ADMIN_USERNAME='admin'
export LOCAL_ADMIN_EMAIL='admin@local'
export LOCAL_ADMIN_PASSWORD='yourpassword'
python scripts/ensure_local_admin.py

# 生产环境
python manage.py createsuperuser
```

7. **启动服务器**
```bash
python manage.py runserver
```

访问：
- 后台管理：http://localhost:8000/admin/
- API 根路径：http://localhost:8000/

## 📚 API 文档

### 快速参考

详细 API 文档请查看：[API Reference](./docs/API_REFERENCE.md)

在线文档与探活（便于前端联调与自动生成客户端）：

- OpenAPI JSON: `GET /docs/schema/`
- Swagger UI: `GET /docs/`
- ReDoc: `GET /docs/redoc/`
- 健康检查: `GET /health/` → `{ "status": "ok" }`
- 服务元信息: `GET /meta/` → `{ service, env }`

### 主要接口

#### 认证
- `POST /oauth/register/` - 注册
- `POST /oauth/login/` - 登录
- `POST /oauth/refresh/` - 刷新 Token

#### 用户
- `GET /users/me/` - 获取当前用户信息
- `PATCH /users/update-profile/` - 更新个人资料
- `POST /users/change-password/` - 修改密码
- `POST /users/upload-avatar/` - 上传头像

#### 报名申请
- `POST /applications/` - 提交报名表
- `GET /applications/my-application/` - 查询我的报名表
- `GET /applications/match-status/` - 查询匹配状态
- `POST /applications/rematch/` - 执行匹配
// 新增：自助匹配能力（每日限次，默认3次）
- `POST /applications/self-match/` - 自助触发匹配
- `GET /applications/self-match/status` - 查询今日已用次数与限额

#### 队伍
- `GET /teams/` - 队伍排行榜
- `GET /teams/my-team/` - 我的队伍
- `POST /teams/disband/` - 解散队伍
- `POST /teams/{id}/complete-task/` - 完成任务

#### 任务
- `GET /tasks/` - 所有任务
- `GET /tasks/active/` - 进行中的任务
- `GET /tasks/upcoming/` - 即将开始的任务
- `GET /tasks/my-completed/` - 已完成的任务

#### 打卡
- `GET /posts/` - 所有打卡记录
- `GET /posts/my-posts/` - 我的打卡记录
- `GET /posts/by-task/` - 按任务查看打卡

## 🧪 测试

### 运行测试

```bash
# 冒烟测试
python scripts/smoke_test.py

# 功能测试
python scripts/test_enhanced_features.py

# 系统检查
python manage.py check
```

### 测试覆盖
- ✅ Admin 登录测试
- ✅ 用户注册/登录测试
- ✅ JWT 认证测试
- ✅ 报名申请流程测试
- ✅ 队伍管理测试
- ✅ 任务系统测试
- ✅ 打卡系统测试

## 📁 项目结构

```
zq_match_backend/
├── server/                 # 主应用目录
│   ├── apps/              # 各功能模块
│   │   ├── users/         # 用户管理
│   │   ├── oauth/         # 认证授权
│   │   ├── academies/     # 院系管理
│   │   ├── applications/  # 报名申请
│   │   ├── teams/         # 队伍管理
│   │   ├── tasks/         # 任务管理
│   │   └── posts/         # 打卡记录
│   ├── settings/          # 配置文件
│   ├── business/          # 业务逻辑
│   └── utils/             # 工具函数
├── scripts/               # 脚本工具
├── docs/                  # 文档
├── static_files/          # 静态文件
└── requirements.txt       # 依赖列表
```

## 🛠️ 技术栈

- **框架**：Django 4.2.6
- **API**：Django REST Framework
- **认证**：Simple JWT
- **数据库**：MySQL / SQLite
- **缓存**：Redis / Local Memory
- **文档**：drf-spectacular (Swagger)
- **工具库**：zq-django-util

## 📖 相关文档

- [功能改进说明](./docs/FEATURE_IMPROVEMENTS.md)
- [API 快速参考](./docs/API_REFERENCE.md)
- [项目总结](./docs/PROJECT_SUMMARY.md)
- [部署指南](./docs/DEPLOYMENT.md)
- [本地管理员创建](./docs/LOCAL_ADMIN.md)
- [前后端联调指南（推荐）](./docs/INTEGRATION_GUIDE.md)

## 🔗 前后端对接说明（简版）

- 认证：JWT（`Authorization: Bearer <token>`）
- 统一返回：
	```json
	{ "code": 0, "msg": "success", "data": { ... }, "errors": null }
	```
- 分页：`data.results`/`data.count`/`data.next`/`data.previous`
- 图片上传：`multipart/form-data` 字段名 `photo`，≤ 5MB，jpg/png/webp
- CORS：开发环境已放开（支持携带凭据与 Authorization）；生产环境继续使用白名单
- 自助匹配：每日默认最多 3 次，超限返回 429；已匹配将直接返回当前队友

更多示例与注意事项请见：[docs/INTEGRATION_GUIDE.md](./docs/INTEGRATION_GUIDE.md)。

## ✅ 合规与安全说明

以上“联调便利性”改动均为行业通用与安全可控做法：
- 文档端点（Swagger/ReDoc/OpenAPI）来源于后端代码自动生成，不额外泄露敏感信息；可按需要在生产环境受控暴露
- 健康/元信息端点仅提供最小必要信息（ok 与 env 标识），不包含内部机密
- 开发环境的 CORS 放开仅在本地生效，生产环境依旧走域名白名单策略
- 自助匹配接口遵循现有权限与业务校验（先报名、每日限次、已匹配短路返回），不会破坏原有流程

因此，将这些内容写入 README 与文档是“合法合规且推荐”的，有助于前后端协作效率与可维护性。

## 🚀 部署

详细部署步骤请参考：[DEPLOYMENT.md](./docs/DEPLOYMENT.md)

### 生产环境配置要点

1. 设置环境变量
2. 配置数据库和 Redis
3. 收集静态文件
4. 配置 Nginx/Gunicorn
5. 设置 HTTPS
6. 配置系统服务

## 🔒 安全注意事项

- ⚠️ 生产环境必须设置 `DEBUG = False`
- ⚠️ 修改 `SECRET_KEY` 为随机值
- ⚠️ 配置 `ALLOWED_HOSTS`
- ⚠️ 启用 HTTPS 相关设置
- ⚠️ 定期更新依赖包

## 📝 更新日志

### v2.1 (2025-10-30)
- 🔧 新增自助匹配接口：`POST /applications/self-match/`、`GET /applications/self-match/status`
- 📘 开放在线文档与探活：`/docs/schema/`、`/docs/`、`/docs/redoc/`、`/health/`、`/meta/`
- 🌐 开发环境放开 CORS 以便本地联调（生产仍白名单）
- 📄 新增《前后端联调指南》文档

### v2.0 (2025-10-29)
- ✨ 新增 14+ 个 API 接口
- 🐛 修复关键 Bug
- 🔒 完善权限控制
- ✅ 添加数据验证
- 📚 完善文档
- 🧪 添加测试覆盖

### v1.0
- 🎉 初始版本发布

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 👥 团队

自强工作室 @ 武汉大学

---

**最后更新**：2025年10月30日