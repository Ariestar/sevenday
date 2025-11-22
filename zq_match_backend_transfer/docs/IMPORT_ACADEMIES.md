# 导入院系数据说明

## 问题说明

后端 `/academies/` 接口返回空数组，原因是数据库中没有院系数据。

## 解决方案

已创建了导入院系数据的管理命令，可以将您提供的所有院系信息导入到数据库中。

## 使用方法

### 方法 1：使用 Django 管理命令（推荐）

```bash
# 导入平级院系数据（所有院系都是顶层，parent=None）
python manage.py import_flat_academies

# 如果需要清空现有数据后重新导入
python manage.py import_flat_academies --clear
```

### 方法 2：使用独立脚本

```bash
# 在项目根目录运行
python scripts/import_flat_academies.py
```

## 导入的院系列表

以下 34 个院系将被导入，所有院系都是平级的（顶层，parent=None）：

1. 文学院
2. 历史学院
3. 哲学学院
4. 外国语言文学学院
5. 新闻与传播学院
6. 艺术学院
7. 信息管理学院
8. 经济与管理学院
9. 法学院
10. 马克思主义学院
11. 社会学院
12. 政治与公共管理学院
13. 教育科学研究院
14. 数学与统计学院
15. 物理科学与技术学院
16. 化学与分子科学学院
17. 生命科学学院
18. 资源与环境科学学院
19. 动力与机械学院
20. 电气与自动化学院
21. 城市设计学院
22. 土木建筑工程学院
23. 水利水电学院
24. 电子信息学院
25. 计算机学院
26. 国家网络安全学院
27. 测绘学院
28. 遥感信息工程学院
29. 基础医学院
30. 健康学院
31. 药学院
32. 口腔医学院
33. 公共卫生学院
34. 护理学院

## API 返回格式

导入数据后，`/academies/` 接口将返回所有院系的平级列表，格式如下：

```json
[
  {
    "id": 1,
    "name": "文学院",
    "parent": null
  },
  {
    "id": 2,
    "name": "历史学院",
    "parent": null
  },
  ...
]
```

## 注意事项

1. 如果数据库中已有院系数据，使用 `update_or_create` 方式，会根据名称更新或创建
2. 使用 `--clear` 选项会先清空所有现有院系数据，请谨慎使用
3. 所有导入的院系的 `level` 字段为 0，`parent` 字段为 null（顶层）

## 相关文件

- 管理命令：`server/apps/academies/management/commands/import_flat_academies.py`
- 独立脚本：`scripts/import_flat_academies.py`
- 视图：`server/apps/academies/views.py`
- 模型：`server/apps/academies/models.py`

