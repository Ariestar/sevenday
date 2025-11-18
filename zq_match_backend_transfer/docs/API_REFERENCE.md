# API 快速参考

## 认证说明

所有需要认证的接口都需要在请求头中携带 JWT Token：
```
Authorization: Bearer {access_token}
```

---

## 1. 用户认证 (OAuth)

### 注册
```http
POST /oauth/register/
Content-Type: application/json

{
    "username": "testuser",
    "email": "user@stu.whu.edu.cn",
    "password": "password123"
}
```

### 登录
```http
POST /oauth/login/
Content-Type: application/json

{
    "email": "user@stu.whu.edu.cn",
    "password": "password123"
}
```

**响应**：
```json
{
    "code": "00000",
    "data": {
        "id": 1,
        "username": "testuser",
        "email": "user@stu.whu.edu.cn",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
}
```

### 刷新 Token
```http
POST /oauth/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## 2. 用户管理 (Users)

### 获取当前用户信息
```http
GET /users/me/
Authorization: Bearer {token}
```

### 更新个人资料
```http
PATCH /users/update-profile/
Authorization: Bearer {token}
Content-Type: application/json

{
    "username": "新昵称",
    "interest": "编程、阅读",
    "grade": 2024
}
```

### 修改密码
```http
POST /users/change-password/
Authorization: Bearer {token}
Content-Type: application/json

{
    "old_password": "old_pass",
    "new_password": "new_pass"
}
```

### 上传头像
```http
POST /users/upload-avatar/
Authorization: Bearer {token}
Content-Type: multipart/form-data

avatar: (binary)
```

### 查看用户详情
```http
GET /users/{user_id}/
Authorization: Bearer {token}
```

---

## 3. 院系 (Academies)

### 获取院系列表
```http
GET /academies/
```

**响应**：
```json
[
    {
        "id": 1,
        "name": "信息管理学院",
        "code": "XXGL"
    }
]
```

---

## 4. 报名申请 (Applications)

### 提交报名表
```http
POST /applications/
Authorization: Bearer {token}
Content-Type: application/json

{
    "my_academy": 1,
    "academy_choice": [2, 3],
    "my_gender": "男",
    "gender_choice": "女",
    "phone": "13800138000",
    "qq": "123456789"
}
```

### 获取我的报名表
```http
GET /applications/my-application/
Authorization: Bearer {token}
```

### 查询匹配状态
```http
GET /applications/match-status/
Authorization: Bearer {token}
```

**响应**：
```json
{
    "is_match": true,
    "team_id": 1,
    "teammates": [
        {
            "id": 2,
            "username": "teammate",
            "avatar": "..."
        }
    ]
}
```

### 执行匹配
```http
POST /applications/rematch/
Authorization: Bearer {token}
```

---

## 5. 队伍 (Teams)

### 获取队伍排行榜
```http
GET /teams/
Authorization: Bearer {token}
```

### 获取我的队伍
```http
GET /teams/my-team/
Authorization: Bearer {token}
```

**响应**：
```json
{
    "id": 1,
    "name": "队伍名称",
    "introduction": "队伍口号",
    "score": 300,
    "members": [
        {
            "id": 1,
            "username": "user1",
            "avatar": "..."
        }
    ],
    "completed_tasks": [
        {
            "id": 1,
            "title": "任务1",
            "score": 100
        }
    ]
}
```

### 更新队伍信息
```http
PATCH /teams/{team_id}/
Authorization: Bearer {token}
Content-Type: application/json

{
    "name": "新队名",
    "introduction": "新口号"
}
```

### 解散队伍
```http
POST /teams/disband/
Authorization: Bearer {token}
```

### 完成任务
```http
POST /teams/{task_id}/complete-task/
Authorization: Bearer {token}
Content-Type: multipart/form-data

title: 打卡标题
description: 打卡描述
photo: (binary)
```

**响应**：
```json
{
    "msg": "任务完成",
    "post": {
        "id": 1,
        "title": "...",
        "photo": "..."
    },
    "current_score": 400
}
```

---

## 6. 任务 (Tasks)

### 获取所有任务
```http
GET /tasks/
Authorization: Bearer {token}
```

### 获取任务详情
```http
GET /tasks/{task_id}/
Authorization: Bearer {token}
```

### 获取进行中的任务
```http
GET /tasks/active/
Authorization: Bearer {token}
```

### 获取即将开始的任务
```http
GET /tasks/upcoming/
Authorization: Bearer {token}
```

### 获取已完成的任务
```http
GET /tasks/my-completed/
Authorization: Bearer {token}
```

**任务响应示例**：
```json
{
    "id": 1,
    "title": "任务标题",
    "cover": "url...",
    "introduction": "任务描述",
    "score": 100,
    "start_time": "2025-01-01",
    "end_time": "2025-01-31",
    "is_active": true,
    "is_expired": false
}
```

---

## 7. 打卡记录 (Posts)

### 获取所有打卡记录
```http
GET /posts/
Authorization: Bearer {token}
```

### 获取我的打卡记录
```http
GET /posts/my-posts/
Authorization: Bearer {token}
```

### 按任务查看打卡
```http
GET /posts/by-task/?task_id=1
Authorization: Bearer {token}
```

### 获取打卡详情
```http
GET /posts/{post_id}/
Authorization: Bearer {token}
```

**打卡记录响应示例**：
```json
{
    "id": 1,
    "title": "打卡标题",
    "description": "打卡描述",
    "photo": "url...",
    "task": 1,
    "task_title": "任务标题",
    "task_score": 100,
    "team": 1,
    "team_name": "队伍名称"
}
```

---

## 8. QQ 绑定

### 绑定 QQ
```http
POST /oauth/bind/qq/
Authorization: Bearer {token}
Content-Type: application/json

{
    "qq": "123456789"
}
```

### 解绑 QQ
```http
POST /oauth/unbind/qq/
Authorization: Bearer {token}
```

---

## 常见状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 204 | 删除成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |

---

## 错误响应格式

```json
{
    "code": "A0001",
    "msg": "参数验证失败",
    "detail": "手机号格式不正确"
}
```

---

## 分页参数

支持分页的接口可使用以下参数：
- `page`: 页码（从1开始）
- `page_size`: 每页数量

示例：
```http
GET /teams/?page=1&page_size=10
```

---

## 筛选和排序

### 筛选示例
```http
GET /posts/?task=1&team=2
```

### 排序示例
```http
GET /tasks/?ordering=-score  # 按分数降序
GET /tasks/?ordering=start_time  # 按开始时间升序
```

---

## 使用示例

### 完整流程示例

#### 1. 用户注册并登录
```bash
# 注册
curl -X POST http://localhost:8000/oauth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@stu.whu.edu.cn","password":"pass123"}'

# 登录
curl -X POST http://localhost:8000/oauth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@stu.whu.edu.cn","password":"pass123"}'
```

#### 2. 提交报名表
```bash
curl -X POST http://localhost:8000/applications/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"my_academy":1,"academy_choice":[2],"my_gender":"男","gender_choice":"女","phone":"13800138000","qq":"123456789"}'
```

#### 3. 执行匹配
```bash
curl -X POST http://localhost:8000/applications/rematch/ \
  -H "Authorization: Bearer {token}"
```

#### 4. 查看我的队伍
```bash
curl -X GET http://localhost:8000/teams/my-team/ \
  -H "Authorization: Bearer {token}"
```

#### 5. 完成任务
```bash
curl -X POST http://localhost:8000/teams/1/complete-task/ \
  -H "Authorization: Bearer {token}" \
  -F "title=完成任务" \
  -F "description=任务描述" \
  -F "photo=@photo.jpg"
```

---

## 注意事项

1. **邮箱验证**：注册时需要使用武汉大学邮箱（@whu.edu.cn 或 @stu.whu.edu.cn）
2. **报名限制**：每个用户只能提交一次报名表
3. **匹配规则**：
   - 双向院系偏好匹配
   - 性别要求匹配（如有）
   - 不会匹配已经匹配过的用户
4. **任务完成**：只有队伍成员可以提交任务打卡
5. **文件上传**：头像和打卡照片建议大小不超过 4MB

---

## 开发环境

### 启动开发服务器
```bash
python manage.py runserver
```

### 运行测试
```bash
python scripts/smoke_test.py
python scripts/test_enhanced_features.py
```

### 系统检查
```bash
python manage.py check
```
