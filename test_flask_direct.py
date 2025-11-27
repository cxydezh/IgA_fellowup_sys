# -*- coding: utf-8 -*-
"""
直接测试Flask应用
"""
import sys
import traceback

# 设置UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    print("=" * 50)
    print("测试Flask应用")
    print("=" * 50)
    
    print("\n导入Flask应用...")
    from app import app
    
    print("\n创建测试客户端...")
    with app.test_client() as client:
        print("\n测试首页路由...")
        response = client.get('/')
        print(f"状态码: {response.status_code}")
        print(f"响应长度: {len(response.data)}")
        
        if response.status_code == 302:
            print("首页重定向正常")
            print(f"重定向到: {response.headers.get('Location', 'N/A')}")
        else:
            print(f"响应内容: {response.data[:500]}")
        
        print("\n测试登录页面...")
        response = client.get('/login')
        print(f"状态码: {response.status_code}")
        print(f"响应长度: {len(response.data)}")
        
        if response.status_code == 200:
            print("登录页面正常")
        else:
            print(f"响应内容: {response.data[:500]}")
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)
    
except Exception as e:
    print(f"\n错误: {e}")
    traceback.print_exc()
    sys.exit(1)




