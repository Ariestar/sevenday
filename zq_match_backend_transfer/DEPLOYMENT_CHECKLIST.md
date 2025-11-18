# 部署检查清单

## 部署前检查

### 1. 代码检查
- [x] QQ登录序列化器已创建
- [x] QQ登录视图已创建  
- [x] URL路由已更新
- [x] 其他登录方式已禁用
- [x] 用户模型QQ字段已修改为unique=True
- [x] 代码语法检查通过

### 2. 数据库迁移准备
- [ ] 在本地生成迁移文件：`python manage.py makemigrations users`
- [ ] 检查迁移文件内容是否正确
- [ ] 备份服务器数据库（重要！）

### 3. 部署步骤
1. **备份服务器数据**
   ```bash
   # 在服务器上备份数据库
   cp db.sqlite3 db.sqlite3.backup
   ```

2. **上传项目文件**
   - 将整个项目文件夹上传到服务器
   - 替换原有项目目录

3. **应用数据库迁移**
   ```bash
   python manage.py migrate
   ```

4. **重启服务**
   ```bash
   # 如果使用Docker
   docker-compose restart
   
   # 如果使用systemd
   sudo systemctl restart your-service-name
   ```

### 4. 部署后验证
- [ ] 测试QQ登录功能：`POST /oauth/qq/`
- [ ] 确认其他登录方式已禁用
- [ ] 检查用户数据完整性
- [ ] 验证JWT token生成正常

### 5. 回滚计划（如果出现问题）
```bash
# 恢复数据库备份
cp db.sqlite3.backup db.sqlite3

# 恢复原项目文件
# 从git或备份中恢复原项目
```

## 注意事项

1. **数据安全**：部署前务必备份数据库
2. **测试环境**：建议先在测试环境验证
3. **用户影响**：QQ字段改为unique后，重复的QQ号会导致迁移失败
4. **服务重启**：部署后需要重启相关服务

## 迁移文件内容预览

生成的迁移文件应该包含：
```python
operations = [
    migrations.AlterField(
        model_name='user',
        name='qq',
        field=models.CharField(max_length=16, unique=True, verbose_name='QQ'),
    ),
]
```
