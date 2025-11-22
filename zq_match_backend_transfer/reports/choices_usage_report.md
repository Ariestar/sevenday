# 院系 / choices 使用扫描报告

生成时间：2025-10-29

概述：本报告列出仓库中关于旧的 `choices`（院系常量）和院系数据的使用与一致性检查结果，以及变更建议。

1) `choices` 定位

- 定义位置：`server/utils/choices.py`（类 `CollegeData`，包含 `college_choices`）
- 搜索结果：仓库中没有其他文件直接引用 `CollegeData.college_choices` 或 `college_choices`（仅在该文件中定义）。

2) 院系数据源对比

- 迁移内数据：`server/apps/academies/migrations/data/zq_academy.json`（用于 migration `0002_data_initial.py`）
- Fixture：`server/fixtures/academies_2025.json`（较新的 authoritative 清单）
- 对比结果：两文件经比较，记录数相同（48 条），相同的 id 集合且对应名称一致（无名称差异）。这说明迁移内的初始数据和 fixture 已同步。

3) 模型与迁移概况

- `academies` app 存在迁移 `0001_initial.py` 和 `0002_data_initial.py`（将初始数据插入）。
- 我新增了幂等的迁移 `0003_update_academies_data.py`，它会从 `server/fixtures/academies_2025.json` 对表记录做 `update_or_create`（按 pk），以确保在已有生产库上也能安全同步数据。

4) 风险评估与建议

- 当前未发现代码仍使用旧整数 choices 做业务逻辑或直接存储（如 models 中使用 `choices=...` 指向 `college_choices`）。因此把院系数据迁移到数据库并维护 fixture 的做法是安全的。
- 建议在部署生产前：
  - 在 staging 上先执行 `python manage.py migrate`，确认 `0003_update_academies_data` 能正常运行且数据结果如预期；
  - 在部署说明中明确：如果生产 DB 已有旧的院系表示（旧 choices 映射），需先运行映射脚本（我可以帮生成）来把旧字段值替换为 academy FK；

5) 结论

- 仓库中院系数据与 fixture 已同步，且没有发现残留的旧 choices 使用点。当前采取的迁移与 fixture 导入策略合适且安全。
