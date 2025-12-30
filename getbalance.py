import json
from schwab.auth import client_from_token_file

# 配置
API_KEY = '1PaQDwtg7K9LYDwMkUzdP66e2kjupAVjXRwGFYFkfKc9z5c4'
APP_SECRET = '7yjAShnMIVcS9zXCxWKe2GqU13OuR68mbLIIiAvQmvqVi1GDYtcKepixGqIo5gln'
TOKEN_PATH = 'token.json'

def get_real_balance():
    try:
        # 1. 初始化（建议开启 enforce_enums=False 以简化字符串操作）
        client = client_from_token_file(
            TOKEN_PATH, API_KEY, APP_SECRET, enforce_enums=False
        )
        
        # 2. 首先获取账户列表，拿到 Account Hash
        print("正在建立连接...")
        acc_nums_resp = client.get_account_numbers()
        if acc_nums_resp.status_code != 200:
            print("无法获取账户哈希，请检查权限。")
            return
            
        account_hash = acc_nums_resp.json()[0]['hashValue']
        
        # 3. 使用特定的 get_account (单数) 接口查询详细余额
        # 这是最稳妥的路径：/accounts/{accountHash}?fields=positions,balances
        print(f"正在查询账户 [{account_hash[:8]}...] 的详细资金...")
        resp = client.get_account(account_hash, fields=['balances', 'positions'])
        
        if resp.status_code != 200:
            # 如果带参数报错，尝试不带参数的纯净调用
            print("带参查询失败，尝试基础查询...")
            resp = client.get_account(account_hash)

        data = resp.json()
        
        # 4. 解析数据 (嘉信返回的单账户数据通常直接在 securitiesAccount 下)
        acc_data = data.get('securitiesAccount', data)
        balances = acc_data.get('currentBalances', {})
        
        print("\n" + "━"*40)
        print(f"💰 账户总资产: ${balances.get('liquidationValue', 0):,.2f}")
        print(f"💵 可用现金:   ${balances.get('cashBalance', 0):,.2f}")
        print(f"🚀 交易购买力: ${balances.get('buyingPower', 0):,.2f}")
        
        # 顺便看看持仓
        positions = acc_data.get('positions', [])
        if positions:
            print(f"📦 当前持仓: {len(positions)} 个标的")
        else:
            print("📦 当前无持仓")
        print("━"*40 + "\n")

    except Exception as e:
        print(f"❌ 运行报错: {e}")

if __name__ == "__main__":
    get_real_balance()