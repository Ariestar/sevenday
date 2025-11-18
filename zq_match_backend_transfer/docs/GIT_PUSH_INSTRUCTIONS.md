# 提交与推送（PowerShell）

下面是一组推荐步骤，用于将本地变更提交到远端并触发 GitHub Actions CI（适用于 Windows PowerShell）。

1. 检查修改

```powershell
# 在仓库根目录运行
git status --porcelain
git add -A
git diff --staged --name-only
```

2. 提交并推送到分支（示例用 feature/academies-update）

```powershell
$branch = 'feature/academies-update'
git checkout -b $branch
git commit -m "Sync academies data: add migration and import command; add CI; harden admin script; add docs"
git push -u origin $branch
```

3. 在 GitHub 上发起 PR 并等待 CI（workflow `CI`）运行。CI 会运行 `python -m compileall .`、`python manage.py check` 与 `python manage.py test`。

4. 合并到 `main` 后，在目标服务器上执行部署步骤（见 `docs/DEPLOYMENT.md`）：

```powershell
# 在服务器上（或通过 CI/CD）
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# 设置生产环境变量（不要在公开 shell 里回显 secret）
python manage.py migrate
python manage.py import_academies
python manage.py collectstatic --noinput
# 启动/重启服务（系统依赖）
```

如果你需要我帮你生成 PR 描述或梳理变更点，我可以把要点格式化成可直接粘贴到 PR 描述里的内容。
