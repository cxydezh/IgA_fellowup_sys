# -*- coding: utf-8 -*-
"""
使用Playwright测试Flask应用（修复版）
"""
from playwright.sync_api import sync_playwright
import time
import sys
import requests

# 设置UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_app():
    """测试应用是否能正常打开"""
    print("=" * 50)
    print("使用Playwright测试Flask应用")
    print("=" * 50)
    
    # 先检查应用是否运行
    print("\n1. 检查Flask应用是否运行...")
    try:
        response = requests.get('http://localhost:5001', timeout=5)
        print(f"   HTTP状态码: {response.status_code}")
        print(f"   Server头: {response.headers.get('Server', 'N/A')}")
        if response.status_code in [200, 302]:
            print("   [OK] Flask应用运行正常")
        else:
            print(f"   [ERROR] Flask应用返回错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [ERROR] 无法连接到Flask应用: {e}")
        print("   请先运行: python start_app.py")
        return False
    
    # 使用Playwright测试
    print("\n2. 使用Playwright测试...")
    try:
        with sync_playwright() as p:
            # 启动浏览器
            print("   启动浏览器...")
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            print("   访问 http://localhost:5001...")
            try:
                # 访问应用
                response = page.goto('http://localhost:5001', timeout=20000, wait_until='domcontentloaded')
                print(f"   HTTP状态码: {response.status if response else 'N/A'}")
                
                # 等待页面加载
                page.wait_for_load_state('networkidle', timeout=10000)
                
                # 检查页面标题
                title = page.title()
                print(f"   页面标题: {title}")
                
                # 检查登录页面元素
                username_input = page.query_selector('input[name="username"]')
                password_input = page.query_selector('input[name="password"]')
                
                if username_input and password_input:
                    print("   [OK] 登录页面加载成功")
                    print("   [OK] 找到用户名输入框")
                    print("   [OK] 找到密码输入框")
                    
                    # 尝试登录
                    print("\n3. 尝试登录...")
                    page.fill('input[name="username"]', 'admin')
                    page.fill('input[name="password"]', 'admin123')
                    page.click('button[type="submit"]')
                    
                    # 等待页面跳转
                    page.wait_for_load_state('networkidle', timeout=10000)
                    time.sleep(2)
                    
                    # 检查是否登录成功
                    current_url = page.url
                    print(f"   当前URL: {current_url}")
                    
                    if 'dashboard' in current_url or '首页' in page.content():
                        print("   [OK] 登录成功！")
                    else:
                        print("   [WARNING] 登录可能失败，检查页面内容...")
                        content_preview = page.content()[:500]
                        print(f"   页面内容预览: {content_preview[:200]}")
                else:
                    print("   [ERROR] 未找到登录表单元素")
                    content_preview = page.content()[:1000]
                    print(f"   页面内容预览: {content_preview[:500]}")
                
                # 截图
                page.screenshot(path='test_screenshot.png')
                print("\n   [OK] 已保存截图: test_screenshot.png")
                
                # 保持浏览器打开一段时间以便查看
                print("\n   浏览器将保持打开5秒...")
                time.sleep(5)
                
                browser.close()
                return True
                
            except Exception as e:
                print(f"   [ERROR] 访问失败: {str(e)}")
                print(f"   错误类型: {type(e).__name__}")
                import traceback
                traceback.print_exc()
                browser.close()
                return False
                
    except Exception as e:
        print(f"   [ERROR] Playwright测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_app()
    
    if success:
        print("\n" + "=" * 50)
        print("测试完成！")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("测试失败！")
        print("=" * 50)
        sys.exit(1)

