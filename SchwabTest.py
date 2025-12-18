from schwab.auth import client_from_manual_flow
from schwab.client import Client
import json

# 配置你的 API 凭据
api_key = '1PaQDwtg7K9LYDwMkUzdP66e2kjupAVjXRwGFYFkfKc9z5c4'
app_secret = '7yjAShnMIVcS9zXCxWKe2GqU13OuR68mbLIIiAvQmvqVi1GDYtcKepixGqIo5gln'
callback_url = 'https://127.0.0.1'
token_path = 'token.json'

def get_client():
    try:
        # 尝试从本地文件加载 token
        client = client_from_manual_flow(api_key, app_secret, callback_url, token_path)
        return client
    except Exception as e:
        print(f"登录失败: {e}")
        return None

client = get_client()

