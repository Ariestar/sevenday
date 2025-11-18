#!/usr/bin/env python
"""
部署前完整性检查脚本
确保所有必要的文件都已准备好
"""

import os
import sys

def check_file_exists(file_path, description):
    """检查文件是否存在"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - 文件不存在")
        return False

def main():
    """主检查函数"""
    print("🔍 检查QQ登录功能部署准备...")
    print("=" * 50)
    
    all_good = True
    
    # 检查核心文件
    files_to_check = [
        ("server/apps/oauth/serializers.py", "QQ登录序列化器"),
        ("server/apps/oauth/views.py", "QQ登录视图"),
        ("server/apps/oauth/urls.py", "URL路由配置"),
        ("server/apps/users/models.py", "用户模型"),
        ("server/apps/users/migrations/0003_alter_user_qq.py", "数据库迁移文件"),
        ("DEPLOYMENT_GUIDE.md", "部署指南"),
        ("deploy_qq_login.sh", "一键部署脚本"),
    ]
    
    for file_path, description in files_to_check:
        if not check_file_exists(file_path, description):
            all_good = False
    
    print("=" * 50)
    
    # 检查关键代码内容
    print("🔍 检查关键代码内容...")
    
    # 检查序列化器中的QQLoginSerializer
    try:
        with open("server/apps/oauth/serializers.py", "r", encoding="utf-8") as f:
            content = f.read()
            if "class QQLoginSerializer" in content:
                print("✅ QQ登录序列化器已定义")
            else:
                print("❌ QQ登录序列化器未找到")
                all_good = False
    except Exception as e:
        print(f"❌ 无法读取序列化器文件: {e}")
        all_good = False
    
    # 检查视图中的QQLoginView
    try:
        with open("server/apps/oauth/views.py", "r", encoding="utf-8") as f:
            content = f.read()
            if "class QQLoginView" in content:
                print("✅ QQ登录视图已定义")
            else:
                print("❌ QQ登录视图未找到")
                all_good = False
    except Exception as e:
        print(f"❌ 无法读取视图文件: {e}")
        all_good = False
    
    # 检查URL配置
    try:
        with open("server/apps/oauth/urls.py", "r", encoding="utf-8") as f:
            content = f.read()
            if 'path("qq/", QQLoginView.as_view()' in content:
                print("✅ QQ登录URL路由已配置")
            else:
                print("❌ QQ登录URL路由未找到")
                all_good = False
    except Exception as e:
        print(f"❌ 无法读取URL文件: {e}")
        all_good = False
    
    # 检查用户模型
    try:
        with open("server/apps/users/models.py", "r", encoding="utf-8") as f:
            content = f.read()
            if 'qq = models.CharField(max_length=16, unique=True' in content:
                print("✅ 用户模型QQ字段已设置为唯一")
            else:
                print("❌ 用户模型QQ字段未设置为唯一")
                all_good = False
    except Exception as e:
        print(f"❌ 无法读取用户模型文件: {e}")
        all_good = False
    
    print("=" * 50)
    
    if all_good:
        print("🎉 所有检查通过！项目已准备好部署")
        print("📝 请按照 DEPLOYMENT_GUIDE.md 进行部署")
        return 0
    else:
        print("❌ 检查未通过，请修复上述问题后再部署")
        return 1

if __name__ == "__main__":
    sys.exit(main())
