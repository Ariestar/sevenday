# 武大邮箱统一登录功能说明

## 功能概述
本项目已更新为统一使用武大邮箱+密码登录，支持QQ号绑定功能，其他登录方式已被禁用。

## 主要变更

### 1. 新增功能
- ✅ 武大邮箱+密码登录（统一登录入口 `POST /oauth/login/`）
- ✅ QQ号绑定功能 (`POST /oauth/bind/qq/`)
- ✅ QQ号解绑功能 (`POST /oauth/unbind/qq/`)
- ✅ 邮箱字段唯一性约束，QQ字段可选绑定
- ✅ 完整的JWT认证系统

### 2. 禁用功能
- ❌ QQ直接登录 (`/oauth/qq/`) - **已移除**
- ❌ 微信登录 (`/oauth/wechat/`)
- ❌ 手机号登录 (`/oauth/phone/`)
- ❌ 自强Auth登录 (`/oauth/zq/`)
- ❌ OpenID登录 (`/oauth/wechat/openid/`)
- ❌ UnionID登录 (`/oauth/zq/unionid/`)

## 登录流程

### 第一步：武大邮箱登录
用户必须使用武大邮箱（@whu.edu.cn 或 @stu.whu.edu.cn）进行登录。

### 第二步：绑定QQ（可选）
登录成功后，用户可以选择绑定QQ号以便后续使用。

## 登录接口

### 武大邮箱登录（统一登录入口）
**请求**：
```http
POST /oauth/login/
Content-Type: application/json

{
    "email": "student@whu.edu.cn",
    "password": "your_password"
}
```

### QQ绑定功能
**绑定QQ**：
```http
POST /oauth/bind/qq/
Content-Type: application/json
Authorization: Bearer YOUR_ACCESS_TOKEN

{
    "qq": "123456789"
}
```

**解绑QQ**：
```http
POST /oauth/unbind/qq/
Content-Type: application/json
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### 响应格式
**登录响应**：
```json
{
    "id": 1,
    "username": "user_name",
    "email": "student@whu.edu.cn",
    "is_authenticated": true,
    "is_staff": false,
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**QQ绑定响应**：
```json
{
    "message": "QQ绑定成功",
    "qq": "123456789"
}
```

**QQ解绑响应**：
```json
{
    "message": "QQ解绑成功",
    "unbound_qq": "123456789"
}
```

## 部署说明

### 快速部署
1. 上传整个项目文件夹到服务器
2. 运行部署脚本：`bash deploy_qq_login.sh`
3. 重启服务

### 详细部署
请查看 `DEPLOYMENT_GUIDE.md` 获取完整的部署说明。

## 注意事项

1. **邮箱要求**：只支持武大邮箱格式（@whu.edu.cn 或 @stu.whu.edu.cn）
2. **QQ绑定**：QQ绑定是可选的，不影响正常使用
3. **安全性**：所有接口都需要JWT认证（除了登录接口）
4. **兼容性**：已移除QQ直接登录功能，确保使用武大邮箱登录

## 文件结构

```
项目根目录/
├── server/
│   ├── apps/
│   │   ├── oauth/
│   │   │   ├── serializers.py    # 包含QQLoginSerializer
│   │   │   ├── views.py          # 包含QQLoginView
│   │   │   └── urls.py           # 仅保留QQ登录路由
│   │   └── users/
│   │       ├── models.py         # QQ字段设置为unique=True
│   │       └── migrations/
│   │           └── 0003_alter_user_qq.py  # 数据库迁移文件
├── DEPLOYMENT_GUIDE.md           # 详细部署指南
├── deploy_qq_login.sh           # 一键部署脚本
├── check_deployment.py          # 部署前检查脚本
└── QQ_LOGIN_README.md           # 本文件
```

## 数据库变更

- `users_user` 表的 `email` 字段现在具有唯一约束
- `users_user` 表的 `qq` 字段现在为可选绑定（可为空）
- 迁移文件：
  - `server/apps/users/migrations/0003_alter_user_qq.py`
  - `server/apps/users/migrations/0004_alter_user_email.py`
  - `server/apps/users/migrations/0005_alter_user_qq_optional.py`

## 注意事项

1. **数据备份**：部署前务必备份数据库
2. **邮箱唯一性**：确保所有用户的邮箱都是唯一的
3. **QQ绑定可选**：QQ号绑定是可选的，用户可以不绑定
4. **服务重启**：部署后必须重启相关服务
5. **测试验证**：部署后务必测试邮箱登录和QQ绑定功能

## 故障排除

### 常见问题

1. **重复QQ号错误**
   - 解决方案：为重复的QQ号添加后缀

2. **迁移失败**
   - 解决方案：检查数据库连接和权限

3. **登录失败**
   - 解决方案：检查QQ号和密码是否正确

### 回滚方案

如果部署出现问题，可以：
1. 恢复数据库备份
2. 恢复原项目文件
3. 重启服务

## 技术支持

如有问题，请查看：
- `DEPLOYMENT_GUIDE.md` - 详细部署指南
- `check_deployment.py` - 部署前检查
- 项目日志文件
