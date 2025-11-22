# 邮箱验证码配置说明

## 功能说明

系统已实现邮箱验证码发送功能，支持两种模式：

1. **真实邮件发送**：配置邮件服务器后，验证码会通过邮件发送到用户邮箱
2. **开发模式**：未配置邮件服务器时，验证码会在控制台输出（便于开发调试）

## 配置方式

### 方式一：环境变量配置（推荐）

在 `.env` 文件或系统环境变量中配置：

```bash
# 邮件服务器配置
EMAIL_HOST=smtp.whu.edu.cn          # SMTP 服务器地址（武大邮箱）
EMAIL_PORT=587                       # SMTP 端口
EMAIL_USE_TLS=True                   # 使用 TLS
EMAIL_USE_SSL=False                  # 不使用 SSL

# 发件人配置
EMAIL_HOST_USER=your_email@whu.edu.cn        # 发件邮箱
EMAIL_HOST_PASSWORD=your_password_or_auth_code  # 邮箱密码或授权码
DEFAULT_FROM_EMAIL=your_email@whu.edu.cn     # 默认发件人
```

### 方式二：直接修改配置文件

编辑 `server/settings/components/email.py`，直接修改配置值。

## 武大邮箱配置示例

### 使用武大邮箱（@whu.edu.cn 或 @stu.whu.edu.cn）

```bash
EMAIL_HOST=smtp.whu.edu.cn
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your_email@whu.edu.cn
EMAIL_HOST_PASSWORD=your_password
DEFAULT_FROM_EMAIL=your_email@whu.edu.cn
```

### 使用其他邮箱服务商

#### QQ 邮箱
```bash
EMAIL_HOST=smtp.qq.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@qq.com
EMAIL_HOST_PASSWORD=授权码（不是密码）
```

#### 163 邮箱
```bash
EMAIL_HOST=smtp.163.com
EMAIL_PORT=25
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@163.com
EMAIL_HOST_PASSWORD=授权码
```

#### Gmail
```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=应用专用密码
```

## 邮件模板

邮件模板位于：
- HTML 模板：`server/templates/email/verify_code.html`
- 文本模板：`server/templates/email/verify_code.txt`

可以根据需要自定义邮件样式和内容。

## 工作流程

1. **已配置邮件服务器**：
   - 生成验证码 → 存储到缓存 → 发送邮件 → 返回成功
   - 开发环境：同时输出到控制台（便于调试）

2. **未配置邮件服务器**：
   - 生成验证码 → 存储到缓存 → 输出到控制台 → 返回成功
   - 适用于开发环境

## 测试

配置完成后，重启 Django 服务器，然后测试发送验证码接口：

```bash
POST /auth/sendCode/
{
  "email": "test@stu.whu.edu.cn"
}
```

如果配置正确，验证码会发送到指定邮箱；如果未配置或发送失败，验证码会在控制台输出。

## 注意事项

1. **授权码 vs 密码**：部分邮箱服务商（如 QQ、163）需要使用授权码而不是登录密码
2. **安全设置**：确保邮箱开启了 SMTP 服务
3. **防火墙**：确保服务器可以访问 SMTP 端口
4. **开发环境**：开发时建议不配置邮件服务器，使用控制台输出更方便
5. **生产环境**：生产环境必须配置邮件服务器，否则用户无法收到验证码

## 故障排查

### 邮件发送失败

1. 检查环境变量是否正确配置
2. 检查邮箱密码/授权码是否正确
3. 检查 SMTP 服务器地址和端口是否正确
4. 检查防火墙是否允许访问 SMTP 端口
5. 查看 Django 日志获取详细错误信息

### 开发环境测试

如果不想配置邮件服务器，可以：
- 不设置 `EMAIL_HOST_USER` 环境变量
- 系统会自动使用控制台输出模式
- 验证码会在后端控制台显示

