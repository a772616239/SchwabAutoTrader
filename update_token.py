#!/usr/bin/env python3
import json
from schwab.auth import client_from_received_url
from unittest.mock import patch

API_KEY = '1PaQDwtg7K9LYDwMkUzdP66e2kjupAVjXRwGFYFkfKc9z5c4'
APP_SECRET = '7yjAShnMIVcS9zXCxWKe2GqU13OuR68mbLIIiAvQmvqVi1GDYtcKepixGqIo5gln'
CALLBACK_URL = 'https://127.0.0.1'
TOKEN_PATH = 'token.json'

def update_token_with_code(auth_url):
    try:
        # 从授权 URL 中提取 state 参数
        import urllib.parse
        parsed_url = urllib.parse.urlparse(auth_url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        state = query_params['state'][0]
        
        # 重新实现 get_auth_context 功能，确保使用相同的 state 参数
        from authlib.integrations.httpx_client import OAuth2Client
        auth_context = type('', (), {})()
        auth_context.callback_url = CALLBACK_URL
        auth_context.oauth = OAuth2Client(API_KEY, redirect_uri=CALLBACK_URL)
        auth_context.authorization_url, auth_context.state = auth_context.oauth.create_authorization_url(
            'https://api.schwabapi.com/v1/oauth/authorize',
            state=state
        )
        
        print(f"✅ 使用的 state 参数: {auth_context.state}")
        
        token_write_func = lambda token: open(TOKEN_PATH, 'w').write(json.dumps(token))
        
        client = client_from_received_url(
            API_KEY, APP_SECRET, auth_context, auth_url, token_write_func, 
            asyncio=False, enforce_enums=True
        )
        
        print("✨ Token 已成功更新！")
        return client
        
    except Exception as e:
        print(f"❌ 更新 Token 失败: {e}")
        print(f"🔍 错误详细信息: {str(type(e))}")
        import traceback
        print(f"📄 堆栈跟踪: {traceback.format_exc()}")
        return None

if __name__ == "__main__":
    # 用户返回的授权回调 URL
    auth_url = "https://127.0.0.1/?code=C0.b2F1dGgyLmJkYy5zY2h3YWIuY29t.WZIbVer1SF0r_WO5rB4dKhKtEKui0ri7Fi6Klt4KumE%40&session=bbaf7fde-3d6e-4e07-ba42-0846201afe61&state=zjlZ0QUwYNVupjinuEKlAHDpiJzHXU"
    
    client = update_token_with_code(auth_url)
    
    if client:
        # 测试 Token 是否有效
        res = client.get_account_numbers()
        print("✅ Token 有效性测试通过")
        print("账户数据:", res.json())
