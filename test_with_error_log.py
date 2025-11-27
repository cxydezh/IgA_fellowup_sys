# -*- coding: utf-8 -*-
"""
测试Flask应用并捕获错误日志
"""
import sys
import subprocess
import time
import requests
import threading

# 设置UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print("=" * 50)
print("测试Flask应用（捕获错误日志）")
print("=" * 50)

# 停止所有Python进程
print("\n1. 停止所有Python进程...")
try:
    subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                   capture_output=True, timeout=5)
except:
    pass

time.sleep(2)

# 启动Flask应用
print("\n2. 启动Flask应用...")
process = subprocess.Popen(
    [sys.executable, 'start_app.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
    universal_newlines=True
)

# 读取输出的线程
output_lines = []
def read_output():
    for line in process.stdout:
        output_lines.append(line)
        print(line, end='')

thread = threading.Thread(target=read_output, daemon=True)
thread.start()

# 等待应用启动
print("\n3. 等待应用启动...")
time.sleep(5)

# 测试应用
print("\n4. 测试应用...")
try:
    response = requests.get('http://localhost:5000', timeout=10)
    print(f"   HTTP状态码: {response.status_code}")
    print(f"   Server头: {response.headers.get('Server', 'N/A')}")
    print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
    print(f"   响应长度: {len(response.text)}")
    
    if response.status_code == 200 or response.status_code == 302:
        print("   [OK] 应用运行正常！")
    else:
        print(f"   [ERROR] 应用返回错误: {response.status_code}")
        if response.text:
            print(f"   响应内容: {response.text[:500]}")
    
    # 测试登录页面
    print("\n5. 测试登录页面...")
    response = requests.get('http://localhost:5000/login', timeout=10)
    print(f"   HTTP状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("   [OK] 登录页面正常！")
    else:
        print(f"   [ERROR] 登录页面返回错误: {response.status_code}")
        if response.text:
            print(f"   响应内容: {response.text[:500]}")
    
except Exception as e:
    print(f"   [ERROR] 测试失败: {e}")
    import traceback
    traceback.print_exc()

# 等待一段时间查看输出
print("\n6. 等待5秒查看应用输出...")
time.sleep(5)

# 停止应用
print("\n7. 停止应用...")
process.terminate()
process.wait()

print("\n" + "=" * 50)
print("测试完成！")
print("=" * 50)




