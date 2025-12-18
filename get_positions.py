from schwab.auth import client_from_token_file
from schwab.client import Client
import json

# Import the Fields enum
from schwab.client import Client

# 1. 基础配置
api_key = '1PaQDwtg7K9LYDwMkUzdP66e2kjupAVjXRwGFYFkfKc9z5c4'
app_secret = '7yjAShnMIVcS9zXCxWKe2GqU13OuR68mbLIIiAvQmvqVi1GDYtcKepixGqIo5gln'
token_path = 'token.json'

def main():
    try:
        client = client_from_token_file(token_path, api_key, app_secret)
    except Exception as e:
        print(f"❌ 加载 Token 失败: {e}")
        return

    # 获取账户哈希
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

    # 获取账户详情，包括持仓
    print("正在获取账户详情...")
    account_resp = client.get_account(account_hash, fields=[Client.Account.Fields.POSITIONS])

    if account_resp.status_code != 200:
        print(f"❌ 无法获取账户详情: {account_resp.status_code} - {account_resp.text}")
        return

    account_data = account_resp.json()
    print("✅ 成功获取账户详情")

    # 解析持仓信息
    positions = account_data.get('securitiesAccount', {}).get('positions', [])
    if not positions:
        print("📭 账户中没有持仓")
        return

    print("\n📊 持仓信息:")
    print("-" * 50)
    for pos in positions:
        instrument = pos.get('instrument', {})
        symbol = instrument.get('symbol', '未知')
        quantity = pos.get('longQuantity', 0) - pos.get('shortQuantity', 0)
        market_value = pos.get('marketValue', 0)
        average_price = pos.get('averagePrice', 0)

        print(f"股票代码: {symbol}")
        print(f"数量: {quantity}")
        print(f"市值: ${market_value:.2f}")
        print(f"平均价格: ${average_price:.2f}")
        print("-" * 30)

if __name__ == "__main__":
    main()