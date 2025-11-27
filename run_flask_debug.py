# -*- coding: utf-8 -*-
"""
运行Flask应用并捕获错误
"""
import sys
import subprocess
import time
import requests

# 设置UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print("=" * 50)
print("运行Flask应用并测试")
print("=" * 50)

# 启动Flask应用
print("\n启动Flask应用...")
process = subprocess.Popen(
    [sys.executable, 'app.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
    universal_newlines=True
)

# 等待应用启动
print("等待应用启动...")
time.sleep(5)

# 读取输出
print("\nFlask应用输出:")
print("-" * 50)

# 测试应用
try:
    print("\n测试应用...")
    response = requests.get('http://localhost:5000', timeout=10)
    print(f"HTTP状态码: {response.status_code}")
    
    if response.status_code == 200 or response.status_code == 302:
        print("应用运行正常！")
    else:
        print(f"应用返回错误: {response.status_code}")
        print(f"响应内容: {response.text[:500]}")
    
    # 测试登录页面
    print("\n测试登录页面...")
    response = requests.get('http://localhost:5000/login', timeout=10)
    print(f"HTTP状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("登录页面正常！")
    else:
        print(f"登录页面返回错误: {response.status_code}")
        print(f"响应内容: {response.text[:500]}")
    
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()

# 读取输出
print("\n读取Flask应用输出...")
for line in process.stdout:
    print(line, end='')
    if 'Running on' in line or 'Error' in line or 'Traceback' in line:
        break

# 保持运行一段时间
print("\n应用将运行10秒...")
time.sleep(10)

# 停止应用
print("\n停止应用...")
process.terminate()
process.wait()

print("\n" + "=" * 50)
print("测试完成！")
print("=" * 50)

