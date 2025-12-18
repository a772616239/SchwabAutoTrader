import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from authlib.integrations.httpx_client import OAuth2Client
from schwab.auth import client_from_manual_flow
from schwab.client import Client

# 1. 你的配置
API_KEY = '1PaQDwtg7K9LYDwMkUzdP66e2kjupAVjXRwGFYFkfKc9z5c4'
APP_SECRET = '7yjAShnMIVcS9zXCxWKe2GqU13OuR68mbLIIiAvQmvqVi1GDYtcKepixGqIo5gln'
CALLBACK_URL = 'https://127.0.0.1'
TOKEN_PATH = 'token.json'

# 注意：修改为你电脑上真实的 Chrome 用户路径，或者先不使用该参数进行测试
CHROME_USER_DATA = f"/Users/{os.getlogin()}/Library/Application Support/Google/Chrome/"

def get_auth_url():
    """使用 schwab-py 内部逻辑构造授权 URL，但不进入 input() 阻塞"""
    oauth = OAuth2Client(API_KEY, redirect_uri=CALLBACK_URL)
    auth_url, _ = oauth.create_authorization_url(
        'https://api.schwabapi.com/v1/oauth/authorize'
    )
    return auth_url

def auto_auth_and_save_token():
    # 1. 获取授权链接
    auth_url = get_auth_url()
    
    # 2. 配置 Selenium
    options = webdriver.ChromeOptions()
    # 如果你想使用现有的登录状态（减少验证码），启用下面这行。
    # 注意：运行前必须关闭所有已打开的 Chrome 窗口，否则会报错。
    options.add_argument(f"--user-data-dir={CHROME_USER_DATA}") 
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        print(f"正在打开授权页面...")
        driver.get(auth_url)
        
        print("="*50)
        print("请在打开的浏览器中完成：\n1. 输入账号密码登录\n2. 完成手机验证码 (MFA)\n3. 点击 'Approve' 授权按钮")
        print("="*50)

        captured_url = ""
        # 3. 循环监控地址栏
        while True:
            try:
                current_url = driver.current_url
                if "code=" in current_url:
                    print("✅ 成功检测到回调 URL，正在截获...")
                    captured_url = current_url
                    break
            except Exception:
                # 窗口关闭或其他异常处理
                break
            time.sleep(1)
            
        if captured_url:
            # 4. 利用 schwab-py 的底层函数将 URL 转换为 Token
            # 这里巧妙地利用手动流，由于我们已经有了 URL，它内部解析后会直接换取 Token
            # 注意：此处需要 mock 掉 input，或者使用内部的 fetch_token 逻辑
            # 最简单的方法是直接调用 client_from_manual_flow，并在提示时粘贴（或模拟输入）
            
            print("正在保存 Token 到文件...")
            # 我们通过这种方式完成最后一步，不用手动去控制台粘贴了
            # 但为了兼容库的逻辑，我们采用最稳妥的方式：
            from unittest.mock import patch
            with patch('builtins.input', return_value=captured_url):
                client = client_from_manual_flow(API_KEY, APP_SECRET, CALLBACK_URL, TOKEN_PATH)
            
            print("✨ Token 已成功更新并保存！")
            return client
            
    finally:
        driver.quit()

def main():
    # 逻辑：先尝试加载，失败则启动 Selenium
    if os.path.exists(TOKEN_PATH):
        try:
            client = client_from_manual_flow(API_KEY, APP_SECRET, CALLBACK_URL, TOKEN_PATH)
            # 测试 Token 是否有效
            resp = client.get_account_numbers()
            if resp.status_code == 200:
                print("✅ 现有 Token 有效，无需重新登录。")
                return client
        except:
            pass
            
    # 需要重新授权
    return auto_auth_and_save_token()

if __name__ == "__main__":
    client = main()
    if client:
        # 测试下单或查询
        res = client.get_account_numbers()
        print("登录后的账户数据:", res.json())