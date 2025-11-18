# Git 提交指令

## 查看变更
```powershell
cd C:\Users\周苹\server_complete_backup\zq_match_backend
git status
git diff
```

## 提交变更（推荐）
```powershell
# 添加所有变更
git add .

# 提交（使用详细的提交信息）
git commit -m "优化: 代码质量、安全性和部署流程改进

主要变更：
- 修复: User模型重复定义导致的AttributeError
- 优化: 院系数据管理（添加幂等迁移0003）
- 新增: CI/CD工作流（.github/workflows/ci.yml）
- 安全: ensure_local_admin.py从环境变量读取凭据
- 安全: debug路由仅在DEBUG模式启用
- 文档: 完善DEPLOYMENT.md和LOCAL_ADMIN.md
- 新增: import_academies管理命令

所有业务功能保持完整（报名、组队、打卡等）
通过Django系统检查（0 issues）"

# 推送到远程仓库
git push origin main
```

## 查看提交历史
```powershell
git log --oneline -10
```

## 如果需要撤销（慎用）
```powershell
# 撤销最后一次提交（保留变更）
git reset --soft HEAD~1

# 撤销最后一次提交（丢弃变更，危险！）
git reset --hard HEAD~1
```

## 创建新分支提交（更安全的方式）
```powershell
# 创建并切换到新分支
git checkout -b optimization-2025-10-29

# 添加并提交
git add .
git commit -m "优化: 代码质量、安全性和部署流程改进"

# 推送到远程新分支
git push origin optimization-2025-10-29

# 在GitHub上创建Pull Request进行代码审查
```

## 验证CI通过后
在GitHub上查看Actions标签页，确认：
- ✅ Python编译检查通过
- ✅ Django系统检查通过  
- ✅ 单元测试通过（如果有数据库权限）

然后可以合并到main分支或直接部署。
