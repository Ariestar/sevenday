# 部署（基础）

本文件给出把项目部署到生产环境的一组推荐步骤和示例配置。根据你的托管方式（裸机、云主机、容器编排等）调整。

## 环境变量（示例）
- DJANGO_ENV=production
- DJANGO_DEBUG=False
- DJANGO_SECRET_KEY=<your secret>
- DATABASE_URL=mysql://user:pass@host:3306/dbname
- REDIS_URL=redis://:password@redis-host:6379/0
- SERVER_URL=https://api.match.example.com
- LOCAL__USERNAME (仅用于 dev)
- LOCAL_ADMIN_PASSWORD (仅用于 dev)

建议使用 secret manager 或 CI/CD 的 secret 注入方式，不要把真实值写入 repo。

## 系统化部署步骤（简要）
1. 更新代码：`git pull origin main`
2. 创建虚拟环境并安装依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. 配置环境变量（生产）并运行迁移：

```powershell
$env:DJANGO_DEBUG='False'; $env:DJANGO_SECRET_KEY='...'; # 以及 DATABASE_URL, REDIS_URL
python manage.py migrate
python manage.py import_academies  # 从 fixture 导入/更新院系数据
python manage.py collectstatic --noinput
```

4. 创建 superuser（通过交互或在 CI 中使用 env 注入并及时更改密码）：

```powershell
python manage.py createsuperuser --username admin --email admin@example.com
```

5. Gunicorn + systemd 示例（Linux 环境示例）

- 创建 systemd unit `/etc/systemd/system/match.service`：

```
[Unit]
Description=Gunicorn for zq_match_backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/repo
Environment="DJANGO_ENV=production"
ExecStart=/path/to/venv/bin/gunicorn server.wsgi:application -w 3 -b unix:/run/match.sock

[Install]
WantedBy=multi-user.target
```

- Nginx 反向代理示例片段：

```
server {
    listen 80;
    server_name api.match.example.com;

    location /static/ {
        alias /path/to/repo/static_files/;
    }

    location / {
        proxy_pass http://unix:/run/match.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 注意事项与故障排查
- 确保 `DJANGO_SECRET_KEY` 在生产中是安全注入的。
- `DJANGO_DEBUG` 必须为 `False`，并设置好 `ALLOWED_HOSTS`。
- 如果迁移在生产上因为数据冲突失败，请确认数据迁移（特别是 `academies`）是否为幂等（建议使用 `manage.py import_academies` 或新的数据迁移）。
- 使用 `journalctl -u match.service -f`（Linux）与 `gunicorn` 日志检查运行时错误。

## 后续改进
- CI 脚本（GitHub Actions）用于自动化测试、打包与部署。
- 把 `import_academies` 包装到部署流水线，确保每次部署后院系数据保持一致。

## 非交互式创建管理员（在 CI / 自动化脚本中）

在 CI 或自动化部署脚本中不建议交互式地创建管理员。两种常见做法：

1. 使用环境变量与临时代码/脚本创建（示例）：

```powershell
# 在 CI secrets 中设置 LOCAL_ADMIN_USERNAME/LOCAL_ADMIN_EMAIL/LOCAL_ADMIN_PASSWORD
setx LOCAL_ADMIN_USERNAME "admin"
setx LOCAL_ADMIN_EMAIL "admin@example.com"
setx LOCAL_ADMIN_PASSWORD "${{ secrets.LOCAL_ADMIN_PASSWORD }}"

python manage.py migrate --noinput
python manage.py import_academies
python scripts/ensure_local_admin.py
```

2. 或者在部署完成后使用 Django shell 执行创建（更可控）：

```powershell
python - <<"PY"
from django.contrib.auth import get_user_model
User = get_user_model()
u = User.objects.filter(username='admin').first()
if not u:
    u = User.objects.create_superuser('admin', 'admin@example.com', 'REPLACE_ME')
else:
    u.set_password('REPLACE_ME')
    u.save()
print('admin created/updated')
PY
```

注意：在 CI/生产环境使用时务必把生产密码放在 secret manager（或 CI secrets）里，并在首次登录后强制修改密码。

## 示例 CI（GitHub Actions）

见仓库 `.github/workflows/ci.yml`，CI 会在 PR 上运行 `python manage.py check` 与 `python manage.py test`，并可扩展为部署流水线。

