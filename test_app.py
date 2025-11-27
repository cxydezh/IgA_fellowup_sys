# -*- coding: utf-8 -*-
"""
使用Playwright测试Flask应用
"""
from playwright.sync_api import sync_playwright
import time
import sys

def test_app():
    """测试应用是否能正常打开"""
    try:
        with sync_playwright() as p:
            # 启动浏览器
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            print("正在访问 http://localhost:5000...")
            try:
                # 访问应用
                response = page.goto('http://localhost:5000', timeout=15000, wait_until='domcontentloaded')
                print(f"HTTP状态码: {response.status}")
                
                if response.status != 200:
                    print(f"错误: HTTP状态码 {response.status}")
                    # 获取错误信息
                    error_text = page.content()
                    print(f"页面内容: {error_text[:1000]}")
                    return False
                
                # 等待页面加载
                page.wait_for_load_state('networkidle', timeout=10000)
                
                # 检查页面标题
                title = page.title()
                print(f"页面标题: {title}")
                
                # 检查是否有错误信息
                error_elements = page.query_selector_all('.alert-danger, .error')
                if error_elements:
                    for elem in error_elements:
                        print(f"发现错误: {elem.inner_text()}")
                
                # 检查登录页面元素
                username_input = page.query_selector('input[name="username"]')
                password_input = page.query_selector('input[name="password"]')
                
                if username_input and password_input:
                    print("登录页面加载成功")
                    print("找到用户名输入框")
                    print("找到密码输入框")
                    
                    # 尝试登录
                    print("\n尝试登录...")
                    page.fill('input[name="username"]', 'admin')
                    page.fill('input[name="password"]', 'admin123')
                    page.click('button[type="submit"]')
                    
                    # 等待页面跳转
                    page.wait_for_load_state('networkidle', timeout=10000)
                    time.sleep(2)
                    
                    # 检查是否登录成功
                    current_url = page.url
                    print(f"当前URL: {current_url}")
                    
                    if 'dashboard' in current_url or '首页' in page.content():
                        print("登录成功！")
                    else:
                        print("登录可能失败，检查页面内容...")
                        content_preview = page.content()[:500]
                        print(f"页面内容预览: {content_preview}")
                else:
                    print("未找到登录表单元素")
                    content_preview = page.content()[:1000]
                    print(f"页面内容预览: {content_preview}")
                
                # 截图
                page.screenshot(path='test_screenshot.png')
                print("\n已保存截图: test_screenshot.png")
                
                # 保持浏览器打开一段时间以便查看
                print("\n浏览器将保持打开5秒...")
                time.sleep(5)
                
                return True
                
            except Exception as e:
                print(f"访问失败: {str(e)}")
                print(f"错误类型: {type(e).__name__}")
                import traceback
                traceback.print_exc()
                return False
            
            finally:
                browser.close()
                
    except Exception as e:
        print(f"Playwright测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("Flask应用测试")
    print("=" * 50)
    print("\n请确保Flask应用正在运行 (python app.py)")
    print("等待3秒后开始测试...\n")
    time.sleep(3)
    
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
