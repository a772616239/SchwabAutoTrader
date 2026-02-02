#!/usr/bin/env python3
from schwab.auth import client_from_token_file
from schwab.client import Client
import json
import os

# 基础配置
API_KEY = '1PaQDwtg7K9LYDwMkUzdP66e2kjupAVjXRwGFYFkfKc9z5c4'
APP_SECRET = '7yjAShnMIVcS9zXCxWKe2GqU13OuR68mbLIIiAvQmvqVi1GDYtcKepixGqIo5gln'
TOKEN_PATH = 'token.json'
TRADES_PATH = 'trades.json'

def main():
    try:
        # 1. 获取认证客户端
        client = client_from_token_file(TOKEN_PATH, API_KEY, APP_SECRET)
        print("✅ 成功加载认证客户端")
    except Exception as e:
        print(f"❌ 加载 Token 失败: {e}")
        return

    # 2. 获取账户哈希
    print("正在获取账户 Hash 映射...")
    numbers_resp = client.get_account_numbers()

    if numbers_resp.status_code != 200:
        print(f"❌ 无法获取账户编号: {numbers_resp.status_code} - {numbers_resp.text}")
        return

    account_numbers = numbers_resp.json()

    try:
        account_hash = account_numbers[0]['hashValue']
        print(f"✅ 成功获取 Hash: {account_hash}")
    except (IndexError, KeyError) as e:
        print(f"❌ 解析 Hash 失败: {e}")
        print("返回数据:", account_numbers)
        return

    # 3. 获取交易记录
    print("正在获取交易记录...")
    transactions_resp = client.get_transactions(account_hash)

    if transactions_resp.status_code != 200:
        print(f"❌ 无法获取交易记录: {transactions_resp.status_code} - {transactions_resp.text}")
        return

    transactions_data = transactions_resp.json()
    print(f"✅ 成功获取 {len(transactions_data)} 条交易记录")

    # 4. 保存到 trades.json
    with open(TRADES_PATH, 'w', encoding='utf-8') as f:
        json.dump(transactions_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 交易记录已保存到 {TRADES_PATH}")

if __name__ == "__main__":
    main()
