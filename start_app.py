# -*- coding: utf-8 -*-
"""
启动Flask应用（单实例）
"""
import sys
import os

# 设置UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 检查端口是否被占用
import socket

def check_port(port):
    """检查端口是否被占用"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

if check_port(5001):
    print("警告: 端口5001已被占用！")
    print("请先停止其他Flask应用实例")
    sys.exit(1)

print("=" * 50)
print("启动Flask应用")
print("=" * 50)
print("\n端口5001可用，正在启动应用...\n")

# 导入并运行Flask应用
from app import app, db
from routes import init_sample_data

# 初始化数据库
with app.app_context():
    try:
        db.create_all()
        print("[OK] 数据库表创建成功")
        # 初始化示例数据
        try:
            init_sample_data()
            print("[OK] 示例数据初始化成功")
        except Exception as e:
            print(f"[WARNING] 示例数据初始化错误: {e}")
            import traceback
            traceback.print_exc()
    except Exception as e:
        print(f"[ERROR] 数据库初始化错误: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 50)
print("Flask应用启动中...")
print("访问地址: http://localhost:5001")
print("按 Ctrl+C 停止应用")
print("=" * 50 + "\n")

# 运行应用（使用5001端口避免冲突）
app.run(debug=True, host='127.0.0.1', port=5001, use_reloader=False)

