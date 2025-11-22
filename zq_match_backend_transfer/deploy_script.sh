#!/bin/bash
# 部署脚本

echo "开始部署QQ登录功能..."

# 1. 备份数据库
echo "备份数据库..."
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)

# 2. 检查重复QQ号
echo "检查重复QQ号..."
python manage.py shell -c "
from users.models import User
from django.db.models import Count
duplicates = User.objects.values('qq').annotate(count=Count('qq')).filter(count__gt=1, qq__isnull=False).exclude(qq='')
if duplicates:
    print('发现重复QQ号:', list(duplicates))
    exit(1)
else:
    print('没有重复QQ号，可以继续迁移')
"

if [ $? -ne 0 ]; then
    echo "发现重复QQ号，请先处理重复数据"
    exit 1
fi

# 3. 处理空QQ号
echo "处理空QQ号..."
python manage.py shell -c "
from users.models import User
users_without_qq = User.objects.filter(qq='')
for user in users_without_qq:
    user.qq = f'temp_{user.id}'
    user.save()
print(f'处理了 {len(users_without_qq)} 个空QQ号')
"

# 4. 应用迁移
echo "应用数据库迁移..."
python manage.py migrate

if [ $? -eq 0 ]; then
    echo "迁移成功！"
    echo "部署完成，请测试QQ登录功能"
else
    echo "迁移失败，请检查错误信息"
    echo "可以恢复备份：cp db.sqlite3.backup.* db.sqlite3"
    exit 1
fi
