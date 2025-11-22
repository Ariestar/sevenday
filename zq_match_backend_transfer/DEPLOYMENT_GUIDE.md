# 武大邮箱统一登录功能部署指南

## 功能概述
- ✅ 统一使用武大邮箱+密码登录
- ✅ 支持QQ号绑定功能（可选）
- ✅ 禁用其他登录方式
- ✅ 邮箱字段设置为唯一约束，QQ字段可选绑定
- ✅ 完整的JWT认证系统

## 部署步骤

### 1. 上传项目文件
将整个项目文件夹上传到服务器，替换原有项目。

### 2. 备份数据库（重要！）
```bash
# 在服务器上执行
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)
```

### 3. 处理数据冲突（如果有）
```bash
# 检查重复QQ号
python manage.py shell -c "
from users.models import User
from django.db.models import Count
duplicates = User.objects.values('qq').annotate(count=Count('qq')).filter(count__gt=1, qq__isnull=False).exclude(qq='')
if duplicates:
    print('发现重复QQ号:', list(duplicates))
else:
    print('没有重复QQ号')
"

# 处理空QQ号
python manage.py shell -c "
from users.models import User
users_without_qq = User.objects.filter(qq='')
for user in users_without_qq:
    user.qq = f'temp_{user.id}'
    user.save()
print(f'处理了 {len(users_without_qq)} 个空QQ号')
"
```

### 4. 应用数据库迁移
```bash
python manage.py migrate
```

### 5. 重启服务
```bash
# 如果使用Docker
docker-compose restart

# 如果使用systemd
sudo systemctl restart your-service-name

# 如果使用其他方式，请重启相应的服务
```

## 验证部署

### 1. 测试武大邮箱登录
```bash
curl -X POST http://your-domain/oauth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@whu.edu.cn",
    "password": "your_password"
  }'
```

### 2. 测试QQ绑定功能
```bash
# 绑定QQ（需要先登录获取token）
curl -X POST http://your-domain/oauth/bind/qq/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "qq": "123456789"
  }'

# 解绑QQ
curl -X POST http://your-domain/oauth/unbind/qq/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. 确认其他登录方式已禁用
```bash
# 这些接口应该返回404或错误
curl -X POST http://your-domain/oauth/wechat/
curl -X POST http://your-domain/oauth/phone/
curl -X POST http://your-domain/oauth/zq/
```

## 回滚方案（如果出现问题）

### 1. 恢复数据库
```bash
cp db.sqlite3.backup.* db.sqlite3
```

### 2. 恢复原项目文件
从备份中恢复原项目文件

## 注意事项

1. **数据安全**：部署前务必备份数据库
2. **QQ号唯一性**：确保所有用户的QQ号都是唯一的
3. **服务重启**：部署后必须重启相关服务
4. **测试验证**：部署后务必测试QQ登录功能

## 新的登录接口

### 武大邮箱登录（统一登录入口）
**接口地址**：`POST /oauth/login/`

**请求格式**：
```json
{
    "email": "student@whu.edu.cn",
    "password": "your_password"
}
```

### QQ绑定功能
**绑定QQ**：`POST /oauth/bind/qq/`
**解绑QQ**：`POST /oauth/unbind/qq/`

**绑定QQ请求格式**：
```json
{
    "qq": "123456789"
}
```

**响应格式**：
```json
{
    "id": 1,
    "username": "user_name",
    "email": "student@whu.edu.cn",
    "qq": "123456789",
    "is_authenticated": true,
    "is_staff": false,
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## 已禁用的登录方式

- ❌ QQ直接登录 (`/oauth/qq/`)
- ❌ 微信登录 (`/oauth/wechat/`)
- ❌ 手机号登录 (`/oauth/phone/`)
- ❌ 自强Auth登录 (`/oauth/zq/`)
- ❌ OpenID登录 (`/oauth/wechat/openid/`)
- ❌ UnionID登录 (`/oauth/zq/unionid/`)

## 数据库变更

- `users_user` 表的 `email` 字段现在具有唯一约束
- `users_user` 表的 `qq` 字段现在为可选绑定（可为空）
- 迁移文件：
  - `server/apps/users/migrations/0003_alter_user_qq.py`
  - `server/apps/users/migrations/0004_alter_user_email.py`
  - `server/apps/users/migrations/0005_alter_user_qq_optional.py`
