# 项目交接与本地运行指南

本文提供一个最简但完整的“压缩源码交付 + 本地运行”的方案，适合 Windows 环境（PowerShell）。如需保留 Git 历史，可改用 git bundle（可选，见文末补充）。

## 交付内容打包（推荐：压缩包方案）

包含这些目录/文件：
- 源码与配置：`server/`, `manage.py`, `pyproject.toml`, `requirements.txt`, `docker-compose.yml`, `Dockerfile`, `config/`, `docs/`, `README.md`
- 迁移：`server/apps/**/migrations/`
- 静态/模板：`static_files/`, `templates/`
- 示例环境变量：`.env.example`
- （可选）数据库与媒体：`db.sqlite3`、`media/`（如果需要带上数据/图片）

排除这些敏感或冗余项：
- `.git/`, `.venv/`, `__pycache__/`, `*.pyc`, 任何真实密钥文件（如 `.env`, `config/production.env`, `*.pem`, `*.key`）

你可以使用脚本 `scripts/package_transfer.ps1` 一键打包（见下）。

## 接收方本地运行步骤（Django 开发模式）

1) 解压压缩包到任意目录（例如 `C:\work\zq_match_backend`）

2) 创建并激活虚拟环境
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3) 安装依赖
```powershell
pip install -r requirements.txt
```

4) 配置环境变量
- 将 `.env.example` 复制为 `.env` 并填写：
  - `DJANGO_SECRET_KEY`：改成随机字符串（生产环境务必更换）
  - `DATABASE_URL`：默认 sqlite 即可（自带 `db.sqlite3` 时可复用）
  - `CACHE_URL`：开发可保持 `locmem:///`，生产建议 Redis
  - `SERVER_URL`：本地可填 `http://localhost:8000`
- 说明：`ALLOWED_HOSTS` 在 `server/settings/environments/*.py` 中定义；如需对接自定义域名，修改对应环境文件或自行扩展从 env 读取。

5) 数据库迁移（若未自带数据）
```powershell
python manage.py migrate
```

6) 收集静态文件（如需）
```powershell
python manage.py collectstatic --noinput
```

7) 创建管理员账号（如需）
```powershell
python manage.py createsuperuser
```

8) 启动服务（开发）
```powershell
python manage.py runserver 0.0.0.0:8000
```

9) 常用检查
- 系统检查：`python manage.py check`
- 文档与健康：
  - OpenAPI/Swagger: `http://localhost:8000/docs`
  - Redoc: `http://localhost:8000/docs/redoc`
  - Schema JSON: `http://localhost:8000/docs/schema`
  - 健康检查: `http://localhost:8000/health`
  - 元信息: `http://localhost:8000/meta`

## 生产环境加固要点（接收方）
- 将 `DJANGO_DEBUG=False`，改强随机的 `DJANGO_SECRET_KEY`
- 设置正确的域名与反向代理（Nginx/Traefik），并配置 `ALLOWED_HOSTS`
- 使用持久型数据库（MySQL/Postgres）：设置 `DATABASE_URL`
- 使用 Redis 作为缓存：设置 `CACHE_URL=redis://...`
- 配置 HTTPS、日志与备份策略
- 若使用 Docker：参考仓库 `docker-compose.yml`、`Dockerfile`

## 一键打包脚本（PowerShell）
运行前请在仓库根目录执行：
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\package_transfer.ps1
```
脚本会：
- 创建临时目录 `transfer_stage/` 并复制源码
- 移除 `.git/`, `.venv/`, `__pycache__/`, `*.pyc`、以及 `.env`、`config/production.env`、`*.key`、`*.pem` 等敏感文件
- 生成 `zq_match_backend_transfer.zip`

## （可选）git bundle 交付（保留历史）
如需保留完整 git 历史，使用：
```powershell
git bundle create ..\zq_match_backend.bundle --all
```
接收方可：
```powershell
git clone ..\zq_match_backend.bundle zq_match_backend
```

## 故障排查速查
- DisallowedHost：请在开发环境中添加 `localhost/127.0.0.1` 到 `ALLOWED_HOSTS`（开发环境文件已包含）或在脚本中临时扩充
- 数据库连接错误：检查 `DATABASE_URL` 格式与网络连通
- 跨域问题：开发环境已放开 CORS；生产需配置白名单
- JWT 相关：确保时钟同步、`SIMPLE_JWT` 配置默认即可

---
交接后请通过安全通道单独传递真实密钥，并在接收方落地后立即轮换（SECRET_KEY、OAuth、第三方服务密钥等）。
