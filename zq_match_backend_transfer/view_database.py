#!/usr/bin/env python
"""
查看数据库内容的脚本
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

def view_database():
    """查看数据库内容"""
    print("=" * 60)
    print("数据库内容查看")
    print("=" * 60)
    
    # 获取数据库配置
    db_config = settings.DATABASES['default']
    db_engine = db_config.get('ENGINE', '')
    db_name = db_config.get('NAME', '')
    
    print(f"\n数据库配置:")
    print(f"  引擎: {db_engine}")
    print(f"  名称: {db_name}")
    
    if 'sqlite' in db_engine.lower():
        print(f"\n数据库文件: {db_name}")
        if not os.path.exists(db_name):
            print("❌ 数据库文件不存在")
            return
        
        file_size = os.path.getsize(db_name)
        print(f"文件大小: {file_size / 1024:.2f} KB")
    
    print("\n" + "=" * 60)
    print("表列表:")
    print("=" * 60)
    
    with connection.cursor() as cursor:
        if 'sqlite' in db_engine.lower():
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [row[0] for row in cursor.fetchall()]
        elif 'mysql' in db_engine.lower():
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
        elif 'postgresql' in db_engine.lower():
            cursor.execute("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY tablename
            """)
            tables = [row[0] for row in cursor.fetchall()]
        else:
            print("❌ 不支持的数据库类型")
            return
        
        if not tables:
            print("数据库中没有表")
            return
        
        for table in tables:
            print(f"\n📊 表: {table}")
            print("-" * 60)
            
            # 获取记录数
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  记录数: {count}")
                
                if count > 0:
                    # 显示前几条记录
                    cursor.execute(f"SELECT * FROM {table} LIMIT 5")
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    
                    print(f"\n  字段: {', '.join(columns)}")
                    print(f"\n  前5条记录:")
                    for i, row in enumerate(rows, 1):
                        print(f"    {i}. {dict(zip(columns, row))}")
            except Exception as e:
                print(f"  ⚠️  查询失败: {e}")
    
    print("\n" + "=" * 60)
    print("使用 Django Shell 查看更详细的内容:")
    print("  py manage.py shell")
    print("  >>> from users.models import User")
    print("  >>> User.objects.all()")
    print("=" * 60)

if __name__ == '__main__':
    view_database()









