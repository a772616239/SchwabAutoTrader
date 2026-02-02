#!/usr/bin/env python3
import json
import httpx
import sys
import time

# 配置
API_KEY = '1PaQDwtg7K9LYDwMkUzdP66e2kjupAVjXRwGFYFkfKc9z5c4'
APP_SECRET = '7yjAShnMIVcS9zXCxWKe2GqU13OuR68mbLIIiAvQmvqVi1GDYtcKepixGqIo5gln'
REDIRECT_URI = 'https://127.0.0.1'
TOKEN_PATH = '/Users/wangxufeng/SchwabAutoTrader/token.json'

redirected_url = sys.argv[1]
# 解析 code
import urllib.parse
query = urllib.parse.urlparse(redirected_url).query
params = urllib.parse.parse_qs(query)
code = params.get('code', [None])[0]

if not code:
    print("ERROR: No code found in URL")
    sys.exit(1)

# 手动换取 token
import base64
auth = base64.b64encode(f"{API_KEY}:{APP_SECRET}".encode()).decode()
headers = {
    'Authorization': f'Basic {auth}',
    'Content-Type': 'application/x-www-form-urlencoded'
}
data = {
    'grant_type': 'authorization_code',
    'code': code,
    'redirect_uri': REDIRECT_URI
}

response = httpx.post('https://api.schwabapi.com/v1/oauth/token', headers=headers, data=data)

if response.status_code == 200:
    token_data = response.json()
    # 按照 schwab-py 的格式保存，包含 expires_at
    token_data['expires_at'] = int(time.time()) + token_data['expires_in']
    with open(TOKEN_PATH, 'w') as f:
        json.dump(token_data, f)
    print("SUCCESS: Token saved to", TOKEN_PATH)
else:
    print(f"ERROR: {response.status_code} - {response.text}")
    sys.exit(1)
