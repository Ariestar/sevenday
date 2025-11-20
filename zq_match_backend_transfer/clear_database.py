#!/usr/bin/env python
"""
清空数据库的脚本
警告：此操作会删除所有数据！
"""
import os
import sys
import django

# 设置 Django 环境
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

django.setup()

from django.conf import settings
from django.db import connection

def clear_database():
    """清空数据库中的所有数据"""
    print("=" * 60)
    print("⚠️  警告：此操作将删除数据库中的所有数据！")
    print("=" * 60)
    
    # 获取数据库配置
    db_config = settings.DATABASES['default']
    db_engine = db_config.get('ENGINE', '')
    db_name = db_config.get('NAME', '')
    
    print(f"\n数据库配置:")
    print(f"  引擎: {db_engine}")
    print(f"  名称: {db_name}")
    
    if 'sqlite' in db_engine.lower():
        # SQLite 数据库
        if os.path.exists(db_name):
            print(f"\n找到 SQLite 数据库文件: {db_name}")
            print("正在删除数据库文件...")
            try:
                os.remove(db_name)
                print(f"✅ 数据库文件已删除: {db_name}")
            except Exception as e:
                print(f"❌ 删除失败: {e}")
        else:
            print(f"\n数据库文件不存在: {db_name}")
    else:
        # MySQL/PostgreSQL 等其他数据库
        print(f"\n检测到非 SQLite 数据库，使用 SQL 清空表...")
        with connection.cursor() as cursor:
            # 获取所有表名
            if 'mysql' in db_engine.lower():
                cursor.execute("SHOW TABLES")
                tables = [row[0] for row in cursor.fetchall()]
            elif 'postgresql' in db_engine.lower():
                cursor.execute("""
                    SELECT tablename FROM pg_tables 
                    WHERE schemaname = 'public'
                """)
                tables = [row[0] for row in cursor.fetchall()]
            else:
                print("❌ 不支持的数据库类型")
                return
            
            # 禁用外键检查（MySQL）
            if 'mysql' in db_engine.lower():
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            # 清空所有表
            for table in tables:
                try:
                    cursor.execute(f"TRUNCATE TABLE {table}")
                    print(f"✅ 已清空表: {table}")
                except Exception as e:
                    print(f"⚠️  清空表 {table} 失败: {e}")
            
            # 重新启用外键检查（MySQL）
            if 'mysql' in db_engine.lower():
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            
            connection.commit()
            print("\n✅ 所有表已清空")
    
    print("\n" + "=" * 60)
    print("下一步：运行迁移重新创建表结构")
    print("  py manage.py migrate")
    print("=" * 60)

if __name__ == '__main__':
    confirm = input("\n确认要删除所有数据吗？(yes/no): ")
    if confirm.lower() == 'yes':
        clear_database()
    else:
        print("操作已取消")

