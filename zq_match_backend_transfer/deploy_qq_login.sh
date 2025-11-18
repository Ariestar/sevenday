#!/bin/bash
# QQ登录功能一键部署脚本

echo "🚀 开始部署QQ登录功能..."

# 1. 备份数据库
echo "📦 备份数据库..."
BACKUP_FILE="db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)"
cp db.sqlite3 "$BACKUP_FILE"
echo "✅ 数据库已备份到: $BACKUP_FILE"

# 2. 检查重复QQ号
echo "🔍 检查重复QQ号..."
python manage.py shell -c "
from users.models import User
from django.db.models import Count
duplicates = User.objects.values('qq').annotate(count=Count('qq')).filter(count__gt=1, qq__isnull=False).exclude(qq='')
if duplicates:
    print('❌ 发现重复QQ号:', list(duplicates))
    exit(1)
else:
    print('✅ 没有重复QQ号')
"

if [ $? -ne 0 ]; then
    echo "❌ 发现重复QQ号，请先处理重复数据"
    echo "💡 建议：为重复的QQ号添加后缀，如 qq_1, qq_2"
    exit 1
fi

# 3. 处理空QQ号
echo "🔧 处理空QQ号..."
python manage.py shell -c "
from users.models import User
users_without_qq = User.objects.filter(qq='')
for user in users_without_qq:
    user.qq = f'temp_{user.id}'
    user.save()
print(f'✅ 处理了 {len(users_without_qq)} 个空QQ号')
"

# 4. 应用数据库迁移
echo "🗄️ 应用数据库迁移..."
python manage.py migrate

if [ $? -eq 0 ]; then
    echo "✅ 数据库迁移成功！"
else
    echo "❌ 数据库迁移失败，请检查错误信息"
    echo "🔄 可以恢复备份：cp $BACKUP_FILE db.sqlite3"
    exit 1
fi

# 5. 重启服务提示
echo "🔄 请重启您的服务："
echo "   - Docker: docker-compose restart"
echo "   - Systemd: sudo systemctl restart your-service-name"
echo "   - 其他方式: 请重启相应的服务"

echo ""
echo "🎉 QQ登录功能部署完成！"
echo "📝 请查看 DEPLOYMENT_GUIDE.md 了解详细使用说明"
echo "🧪 请测试登录接口：POST /oauth/qq/"
