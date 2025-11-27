# -*- coding: utf-8 -*-
"""
检查Flask应用是否能正常运行
"""
import requests
import time
import sys

def check_app():
    """检查应用是否能正常响应"""
    url = 'http://localhost:5000'
    
    print("等待应用启动...")
    time.sleep(3)
    
    try:
        print(f"正在访问 {url}...")
        response = requests.get(url, timeout=10)
        print(f"HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("应用运行正常！")
            print(f"响应内容长度: {len(response.text)} 字符")
            print(f"响应内容预览:\n{response.text[:500]}")
            return True
        else:
            print(f"应用返回错误状态码: {response.status_code}")
            print(f"响应内容: {response.text[:1000]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("无法连接到应用，请确保应用正在运行")
        return False
    except Exception as e:
        print(f"检查失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("检查Flask应用")
    print("=" * 50)
    
    success = check_app()
    
    if not success:
        print("\n尝试直接运行Flask应用查看错误...")
        print("请运行: python app.py")
        sys.exit(1)




