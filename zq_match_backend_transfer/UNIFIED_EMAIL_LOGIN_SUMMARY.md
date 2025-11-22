# 武大邮箱统一登录功能实现总结

## 🎯 功能概述

已成功将系统修改为统一使用武大邮箱登录，并添加QQ绑定功能：

- ✅ **统一登录入口**：仅支持武大邮箱+密码登录
- ✅ **QQ绑定功能**：用户登录后可选择绑定QQ号
- ✅ **QQ解绑功能**：用户可以解绑已绑定的QQ号
- ❌ **QQ直接登录已移除**：不再支持QQ号+密码直接登录
- ❌ 其他登录方式已禁用

## 📝 主要修改文件

### 1. 核心功能文件

#### `server/apps/oauth/serializers.py`
- ✅ 添加了 `QQBindSerializer` 类（QQ绑定序列化器）
- ✅ 添加了 `QQUnbindSerializer` 类（QQ解绑序列化器）
- ✅ 保留 `EmailLoginSerializer` 类（武大邮箱登录）
- ❌ 移除了 `QQLoginSerializer` 类（QQ直接登录）

#### `server/apps/oauth/views.py`
- ✅ 添加了 `QQBindView` 类（QQ绑定视图）
- ✅ 添加了 `QQUnbindView` 类（QQ解绑视图）
- ✅ 保留 `EmailLoginView` 类（武大邮箱登录视图）
- ❌ 移除了 `QQLoginView` 类（QQ直接登录视图）
- ✅ 添加了 `APIView` 导入

#### `server/apps/oauth/urls.py`
- ✅ 修改登录入口为 `path("login/", EmailLoginView.as_view(), name="email_login")`
- ✅ 添加了 `path("bind/qq/", QQBindView.as_view(), name="qq_bind")`
- ✅ 添加了 `path("unbind/qq/", QQUnbindView.as_view(), name="qq_unbind")`
- ❌ 完全移除了QQ直接登录路由和相关导入

#### `server/apps/users/models.py`
- ✅ 修改QQ字段：`qq = models.CharField(max_length=16, unique=True, blank=True, null=True, verbose_name="QQ")`
- ✅ QQ字段现在为可选绑定（可为空）

### 2. 数据库迁移文件

#### `server/apps/users/migrations/0005_alter_user_qq_optional.py`
- ✅ 新创建的迁移文件
- ✅ 将QQ字段设置为可选（blank=True, null=True）

### 3. 文档更新

#### `DEPLOYMENT_GUIDE.md`
- ✅ 更新为武大邮箱统一登录
- ✅ 添加了QQ绑定功能说明
- ✅ 更新了测试示例

#### `QQ_LOGIN_README.md`
- ✅ 重命名为武大邮箱统一登录
- ✅ 添加了QQ绑定和解绑接口说明
- ✅ 更新了注意事项

## 🔧 技术实现

### 统一登录入口
- **登录接口**：`POST /oauth/login/`
- **请求格式**：
```json
{
    "email": "student@whu.edu.cn",
    "password": "your_password"
}
```

### QQ绑定功能
- **绑定接口**：`POST /oauth/bind/qq/`
- **解绑接口**：`POST /oauth/unbind/qq/`
- **需要JWT认证**：绑定和解绑操作需要用户先登录

### 邮箱格式验证
```python
def validate_email(self, value):
    """验证武大邮箱格式"""
    if not (value.endswith('@whu.edu.cn') or value.endswith('@stu.whu.edu.cn')):
        raise serializers.ValidationError("请输入有效的武大邮箱")
    return value
```

### QQ格式验证
```python
def validate_qq(self, value):
    """验证QQ号格式"""
    import re
    if not re.match(r'^\d{5,16}$', value):
        raise serializers.ValidationError("QQ号格式不正确")
    return value
```

## 🗄️ 数据库变更

### 字段修改
- `users_user.email` → 添加 `unique=True` 约束
- `users_user.qq` → 修改为可选绑定（`blank=True, null=True`）

### 迁移文件
- `0003_alter_user_qq.py` - QQ字段唯一约束
- `0004_alter_user_email.py` - 邮箱字段唯一约束
- `0005_alter_user_qq_optional.py` - QQ字段可选绑定

## 🚀 部署说明

### 部署步骤
1. 上传整个项目文件夹到服务器
2. 备份数据库：`cp db.sqlite3 db.sqlite3.backup`
3. 应用迁移：`python manage.py migrate`
4. 重启服务：`docker-compose restart`

### 验证测试
```bash
# 1. 测试武大邮箱登录
curl -X POST http://your-domain/oauth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "student@whu.edu.cn", "password": "your_password"}'

# 2. 测试QQ绑定（需要先登录获取token）
curl -X POST http://your-domain/oauth/bind/qq/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"qq": "123456789"}'

# 3. 测试QQ解绑
curl -X POST http://your-domain/oauth/unbind/qq/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 📊 接口说明

### 登录接口
- **URL**：`POST /oauth/login/`
- **功能**：武大邮箱+密码登录
- **返回**：JWT token和用户信息

### QQ绑定接口
- **URL**：`POST /oauth/bind/qq/`
- **功能**：绑定QQ号到当前用户
- **认证**：需要JWT token
- **限制**：每个用户只能绑定一个QQ号

### QQ解绑接口
- **URL**：`POST /oauth/unbind/qq/`
- **功能**：解绑当前用户的QQ号
- **认证**：需要JWT token

## ⚠️ 注意事项

1. **数据备份**：部署前务必备份数据库
2. **邮箱唯一性**：确保所有用户的邮箱都是唯一的
3. **QQ绑定可选**：QQ号绑定是可选的，用户可以不绑定
4. **服务重启**：部署后必须重启相关服务
5. **测试验证**：部署后务必测试邮箱登录和QQ绑定功能

## 📊 修改统计

| 文件类型 | 修改数量 | 说明 |
|---------|---------|------|
| **核心功能文件** | 4个 | 实现统一邮箱登录和QQ绑定 |
| **数据库文件** | 1个 | QQ字段可选绑定迁移 |
| **文档文件** | 2个 | 更新部署和说明文档 |
| **总计** | **7个文件** | 功能实现+文档更新 |

## ✅ 功能验证

- ✅ 武大邮箱统一登录
- ✅ QQ绑定功能
- ✅ QQ解绑功能
- ✅ JWT认证系统
- ✅ 数据库约束
- ✅ 部署文档完整

## 🎉 总结

现在系统完全支持武大邮箱统一登录，用户必须使用武大邮箱进行登录，登录后可以选择绑定QQ号。QQ直接登录功能已被完全移除，这确保了身份认证的统一性和安全性，同时保持了QQ绑定的灵活性！

### 主要改进：
1. **统一身份认证**：所有用户必须使用武大邮箱登录
2. **简化登录流程**：移除了QQ直接登录的复杂性
3. **保持灵活性**：用户仍可选择绑定QQ号
4. **提高安全性**：减少了多种登录方式带来的安全风险
