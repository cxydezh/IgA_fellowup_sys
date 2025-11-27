# -*- coding: utf-8 -*-
"""
运行Flask应用并测试
"""
import subprocess
import time
import requests
import sys
import threading

def run_flask():
    """运行Flask应用"""
    try:
        process = subprocess.Popen(
            [sys.executable, 'app.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        return process
    except Exception as e:
        print(f"启动Flask应用失败: {e}")
        return None

def test_app():
    """测试应用"""
    url = 'http://localhost:5000'
    
    print("等待应用启动...")
    time.sleep(5)
    
    try:
        print(f"正在访问 {url}...")
        response = requests.get(url, timeout=10)
        print(f"HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("应用运行正常！")
            return True
        else:
            print(f"应用返回错误状态码: {response.status_code}")
            print(f"响应内容:\n{response.text[:1000]}")
            return False
            
    except Exception as e:
        print(f"测试失败: {e}")
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("运行并测试Flask应用")
    print("=" * 50)
    
    # 启动Flask应用
    process = run_flask()
    
    if process:
        try:
            # 读取输出
            print("\nFlask应用输出:")
            print("-" * 50)
            
            # 在后台读取输出
            def read_output():
                for line in process.stdout:
                    print(line, end='')
            
            thread = threading.Thread(target=read_output, daemon=True)
            thread.start()
            
            # 等待并测试
            time.sleep(3)
            success = test_app()
            
            if success:
                print("\n" + "=" * 50)
                print("测试成功！")
                print("=" * 50)
            else:
                print("\n" + "=" * 50)
                print("测试失败！")
                print("=" * 50)
            
            # 保持运行一段时间
            print("\n应用将运行10秒...")
            time.sleep(10)
            
        finally:
            process.terminate()
            process.wait()
    else:
        print("无法启动Flask应用")
        sys.exit(1)




