# -*- coding: utf-8 -*-
"""
调试Flask应用
"""
import sys
import traceback

try:
    print("=" * 50)
    print("调试Flask应用")
    print("=" * 50)
    
    print("\n1. 导入Flask应用...")
    from app import app
    print("   [OK] Flask应用导入成功")
    
    print("\n2. 检查数据库...")
    from database import db
    with app.app_context():
        try:
            db.create_all()
            print("   [OK] 数据库创建成功")
        except Exception as e:
            print(f"   [ERROR] 数据库创建失败: {e}")
            traceback.print_exc()
    
    print("\n3. 检查路由...")
    from routes import index, login, dashboard
    print("   [OK] 路由导入成功")
    
    print("\n4. 测试客户端...")
    with app.test_client() as client:
        print("   [OK] 测试客户端创建成功")
        
        print("\n5. 测试首页路由...")
        try:
            response = client.get('/')
            print(f"   HTTP状态码: {response.status_code}")
            if response.status_code == 302:  # 重定向
                print("   [OK] 首页路由正常（重定向到登录页）")
            else:
                print(f"   [ERROR] 意外的状态码: {response.status_code}")
                print(f"   响应内容: {response.data[:500]}")
        except Exception as e:
            print(f"   [ERROR] 首页路由测试失败: {e}")
            traceback.print_exc()
        
        print("\n6. 测试登录页面...")
        try:
            response = client.get('/login')
            print(f"   HTTP状态码: {response.status_code}")
            if response.status_code == 200:
                print("   [OK] 登录页面正常")
            else:
                print(f"   [ERROR] 登录页面返回错误: {response.status_code}")
                print(f"   响应内容: {response.data[:500]}")
        except Exception as e:
            print(f"   [ERROR] 登录页面测试失败: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("调试完成！")
    print("=" * 50)
    
except Exception as e:
    print(f"\n[ERROR] 调试失败: {e}")
    traceback.print_exc()
    sys.exit(1)

