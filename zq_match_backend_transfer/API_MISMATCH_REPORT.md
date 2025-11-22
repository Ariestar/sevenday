# API 接口不匹配报告

## 前端调用但后端缺失的接口

### 1. 认证相关 (auth.js)
- ❌ `POST /auth/wxLogin` - 微信登录（前端调用但后端没有实现）

### 2. 报名相关 (signup.js)
- ❌ `POST /signup/update/` - 更新报名信息（前端调用但后端没有实现）
- ❌ `GET /signup/status/` - 检查报名状态（前端调用但后端没有实现）

### 3. 广场相关 (square.js)
- ❌ `GET /api/square/list` - 获取广场列表（前端调用但后端没有实现）
- ❌ `POST /api/square/like` - 点赞/取消点赞（前端调用但后端没有实现）
- ❌ `GET /api/square/detail` - 获取广场详情（前端调用但后端没有实现）
- ❌ `POST /api/square/comment` - 提交评论（前端调用但后端没有实现）

### 4. 上传相关 (upload.js)
- ❌ `POST /upload/avatar` - 上传头像（前端调用 `/upload/avatar`，后端实际是 `/users/upload-avatar/`）
- ❌ `POST /upload/checkin` - 上传打卡图片（前端调用但后端没有实现）

## 已匹配的接口 ✅

### 认证相关
- ✅ `POST /auth/sendCode/` → `POST /auth/sendCode/`
- ✅ `POST /auth/verify/` → `POST /auth/verify/`
- ✅ `GET /auth/userInfo/` → `GET /auth/userInfo/`
- ✅ `POST /auth/updateUserInfo/` → `POST /auth/updateUserInfo/`

### 报名相关
- ✅ `POST /signup/` → `POST /signup/` (ApplicationViewSet.create)
- ✅ `GET /signup/detail/` → `GET /signup/detail/` (ApplicationViewSet.signup_detail)

### 匹配相关
- ✅ `POST /match/auto/` → `POST /match/auto/`
- ✅ `POST /match/target/` → `POST /match/target/`
- ✅ `POST /match/confirm/` → `POST /match/confirm/`
- ✅ `GET /match/list/` → `GET /match/list/`
- ✅ `GET /match/team/` → `GET /match/team/`
- ✅ `POST /match/teamName/` → `POST /match/teamName/`
- ✅ `POST /match/disband/` → `POST /match/disband/`
- ✅ `GET /match/checkDisband/` → `GET /match/checkDisband/`
- ✅ `POST /match/expectation/` → `POST /match/expectation/`
- ✅ `GET /match/expectation/` → `GET /match/expectation/`

### 打卡相关
- ✅ `GET /api/checkin/tasks/` → `GET /api/checkin/tasks/`
- ✅ `POST /api/checkin/submit/` → `POST /api/checkin/submit/`
- ✅ `GET /api/checkin/detail/` → `GET /api/checkin/detail/`
- ✅ `GET /api/checkin/myList/` → `GET /api/checkin/myList/`
- ✅ `GET /api/checkin/teammateList/` → `GET /api/checkin/teammateList/`
- ✅ `POST /api/checkin/resubmit/` → `POST /api/checkin/resubmit/`

## 已修复的问题 ✅

1. **上传接口路径**：
   - ✅ 已添加 `POST /upload/avatar` 路由（映射到 UserView.upload_avatar）
   - ✅ 已添加 `POST /upload/checkin` 路由（映射到 PostViewSet.checkin_upload_image）

2. **报名相关接口**：
   - ✅ 已添加 `POST /signup/update/` 接口（ApplicationViewSet.signup_update）
   - ✅ 已添加 `GET /signup/status/` 接口（ApplicationViewSet.signup_status）

## 已实现的接口 ✅

### 广场相关接口
- ✅ `GET /api/square/list` - 获取广场列表（PostViewSet.square_list）
- ✅ `POST /api/square/like` - 点赞/取消点赞（PostViewSet.square_like）
- ✅ `GET /api/square/detail` - 获取广场详情（PostViewSet.square_detail）
- ✅ `POST /api/square/comment` - 提交评论（PostViewSet.square_comment）

### 微信登录接口
- ✅ `POST /auth/wxLogin/` - 微信登录（WxLoginView）
- ✅ `POST /auth/wxLogin` - 微信登录（无斜杠版本）

## 新增的数据模型

1. **PostLike** - 打卡点赞表
   - 字段：post, user, create_time
   - 唯一约束：每个用户对每个打卡只能点赞一次

2. **PostComment** - 打卡评论表
   - 字段：post, user, content, create_time, update_time

3. **Post模型更新**
   - 添加了 create_time 和 update_time 字段

