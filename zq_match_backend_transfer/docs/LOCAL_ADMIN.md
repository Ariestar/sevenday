# 本地管理员账号创建（安全说明）

此文档说明如何在本地开发环境创建或更新超级管理员账号，以及安全建议。

注意：仓库中保留的 `scripts/ensure_local_admin.py` 是开发辅助脚本，包含示例密码，已被加入 `.gitignore`。不要在公共仓库中提交真实凭据。

推荐流程（本地开发、临时使用）：

1. 使用 Django 自带命令交互式创建（推荐）：

```powershell
python manage.py createsuperuser --username admin --email admin@example.com
```

此命令会提示你设置密码并不会把凭据写入版本控制。

2. 使用仓库内的脚本（仅限离线、本地开发、并且在你确认脚本来源可信的情况下）：

```powershell
python scripts/ensure_local_admin.py
```

该脚本会创建或更新 `admin` 用户并设置密码。因为脚本可能包含明文密码，请避免将脚本或密码提交到远程仓库；仓库已将该脚本加入 `.gitignore`。

3. 安全建议：
- 在生产环境不要使用固定脚本或明文密码创建管理员；生产请使用 `createsuperuser` 或通过运维流程安全注入随机密码并在首次登录后变更密码。
- 如果必须用脚本创建账号，请将凭据通过安全渠道（例如 Vault、环境变量或 CI secret）注入，并在创建后删除凭据来源。
- 确保 `DEBUG=False` 与合适的 `ALLOWED_HOSTS` 在部署前设置好。

如果需要，我可以把 `scripts/ensure_local_admin.py` 改为读取环境变量（更安全），并把示例放入 `docs/`，由你决定是否继续。
