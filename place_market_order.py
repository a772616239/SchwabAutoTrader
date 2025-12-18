from schwab.auth import client_from_token_file
from schwab.client import Client
from schwab.orders.equities import equity_buy_market
from schwab.orders.common import Duration, Session
import json

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

    # --- 核心修复部分：改用 get_account_numbers() ---
    print("正在获取账户 Hash 映射...")
    numbers_resp = client.get_account_numbers()
    
    if numbers_resp.status_code != 200:
        print(f"❌ 无法获取账户编号: {numbers_resp.status_code} - {numbers_resp.text}")
        return

    account_numbers = numbers_resp.json()
    
    # 打印一下结构方便你确认
    # print(json.dumps(account_numbers, indent=2))

    try:
        # 这个接口返回的是一个列表，每个元素包含 'accountNumber' 和 'hashValue'
        # 我们取第一个账户
        account_hash = account_numbers[0]['hashValue']
        print(f"✅ 成功获取 Hash: {account_hash}")
    except (IndexError, KeyError) as e:
        print(f"❌ 解析 Hash 失败: {e}")
        print("返回数据:", account_numbers)
        return

    # 4. 构建订单：买入 1 股 NVDA 市价单
    symbol = 'NVDA'
    quantity = 1
    
    # 再次提醒：现在是美股盘后时间，市价单可能会被拒绝
    # 如果报错 "Individual orders of this type are not allowed"，请换成限价单
    order_spec = equity_buy_market(symbol, quantity) \
        .set_duration(Duration.DAY) \
        .set_session(Session.NORMAL) \
        .build()

    # 5. 提交订单
    print(f"🚀 正在尝试下单: 买入 {quantity} 股 {symbol}...")
    # order_resp = client.place_order(account_hash, order_spec)

    # if order_resp.status_code in [200, 201, 202]:
    #     print("✨ 成功！订单已提交。")
    #     location = order_resp.headers.get('location', '')
    #     print(f"订单查询路径: {location}")
    # else:
    #     print(f"🛑 下单失败！状态码: {order_resp.status_code}")
    #     print(f"错误原因: {order_resp.text}")

if __name__ == "__main__":
    main()