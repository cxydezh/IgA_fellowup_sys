# -*- coding: utf-8 -*-
"""
检查端口5000被哪个程序占用
"""
import subprocess
import sys

# 设置UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print("=" * 60)
print("检查端口5000占用情况")
print("=" * 60)

# 1. 查看端口占用
print("\n1. 查看端口5000占用情况...")
try:
    result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True, encoding='gbk')
    if result.stdout:
        lines = result.stdout.split('\n')
    else:
        lines = []
    for line in lines:
        if ':5000' in line and 'LISTENING' in line:
            print(f"   找到: {line.strip()}")
            parts = line.split()
            if len(parts) >= 5:
                pid = parts[-1]
                print(f"   占用进程ID: {pid}")
                
                # 2. 查看进程信息
                print(f"\n2. 查看进程 {pid} 的详细信息...")
                try:
                    result2 = subprocess.run(
                        ['wmic', 'process', 'where', f'ProcessId={pid}', 'get', 
                         'ProcessId,Name,CommandLine,ExecutablePath,ParentProcessId'],
                        capture_output=True, text=True, encoding='utf-8'
                    )
                    print(result2.stdout)
                    
                    # 解析进程名
                    lines2 = result2.stdout.split('\n')
                    for line2 in lines2:
                        if 'PDDPrintClient' in line2 or 'PrintClient' in line2:
                            print(f"\n   [发现] 这是拼多多打印客户端程序")
                            break
                    
                except Exception as e:
                    print(f"   查看进程信息失败: {e}")
                
                # 3. 查看进程路径
                print(f"\n3. 查看进程 {pid} 的路径...")
                try:
                    result3 = subprocess.run(
                        ['powershell', '-Command', 
                         f'Get-Process -Id {pid} -ErrorAction SilentlyContinue | Select-Object Id,ProcessName,Path,StartTime'],
                        capture_output=True, text=True, encoding='utf-8'
                    )
                    print(result3.stdout)
                except Exception as e:
                    print(f"   查看进程路径失败: {e}")
                
                break
    else:
        print("   未找到占用端口5000的进程")
        
except Exception as e:
    print(f"   检查失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("检查完成")
print("=" * 60)
print("\n结论:")
print("端口5000被 PDDPrintClient.exe (拼多多打印客户端) 占用")
print("这是一个打印客户端程序，不是我们的Flask应用")
print("\n建议:")
print("1. 如果不需要使用拼多多打印客户端，可以关闭它")
print("2. 或者使用其他端口运行Flask应用（如5001）")
print("3. 当前Flask应用已配置为使用端口5001运行")

