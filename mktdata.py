from schwab.auth import client_from_token_file
from schwab.client import Client
import json
import sys

# ==========================================
# 1. 核心配置（请替换为你自己的真实 Key）
# ==========================================
# API_KEY = '你的_API_KEY_在这里'
# APP_SECRET = '你的_APP_SECRET_在这里'
API_KEY = '1PaQDwtg7K9LYDwMkUzdP66e2kjupAVjXRwGFYFkfKc9z5c4'
APP_SECRET = '7yjAShnMIVcS9zXCxWKe2GqU13OuR68mbLIIiAvQmvqVi1GDYtcKepixGqIo5gln'
TOKEN_PATH = 'token.json'  # 确保此文件与脚本在同一目录，或提供完整路径

def get_schwab_client():
    """初始化并返回 API 客户端"""
    try:
        # 该函数会自动处理 Token 刷新
        client = client_from_token_file(TOKEN_PATH, API_KEY, APP_SECRET)
        return client
    except FileNotFoundError:
        print(f"❌ 错误: 找不到 {TOKEN_PATH} 文件。请先运行授权流程生成 Token。")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 认证失败: {e}")
        sys.exit(1)

def get_account_positions(client):
    """获取并打印所有持仓信息"""
    print("\n--- 正在获取账户持仓 ---")
    
    # 步骤 A: 获取账户 Hash 值
    num_resp = client.get_account_numbers()
    if num_resp.status_code != 200:
        print(f"无法获取账户列表: {num_resp.text}")
        return
    
    # 获取第一个有效账户的 Hash
    accounts = num_resp.json()
    account_hash = accounts[0]['hashValue']
    print(f"✅ 成功锁定账户 (Hash末尾): ...{account_hash[-5:]}")

    # 步骤 B: 获取该账户的详细持仓
    # fields=[Client.Account.Fields.POSITIONS] 是必须的，否则不返回持仓列表
    acc_resp = client.get_account(account_hash, fields=[Client.Account.Fields.POSITIONS])
    
    if acc_resp.status_code == 200:
        data = acc_resp.json()
        positions = data.get('securitiesAccount', {}).get('positions', [])
        
        if not positions:
            print("📭 当前账户没有持仓。")
            return

        print(f"{'代码':<8} | {'数量':<10} | {'市值':<12} | {'平均成本':<10}")
        print("-" * 50)
        for pos in positions:
            symbol = pos['instrument']['symbol']
            qty = pos.get('longQuantity', 0) - pos.get('shortQuantity', 0)
            val = pos.get('marketValue', 0)
            price = pos.get('averagePrice', 0)
            print(f"{symbol:<8} | {qty:<10,.2f} | ${val:<11,.2f} | ${price:<10,.2f}")
    else:
        print(f"❌ 获取详情失败: {acc_resp.status_code}")

def get_market_quote(client, symbol):
    """查询指定股票的实时行情"""
    print(f"\n--- 正在查询行情: {symbol} ---")
    resp = client.get_quote(symbol)
    
    if resp.status_code == 200:
        data = resp.json().get(symbol, {})
        quote = data.get('quote', {})
        ref = data.get('reference', {})
        
        print(f"股票名称: {ref.get('description', 'N/A')}")
        print(f"当前价格: ${quote.get('lastPrice', 0):.2f}")
        print(f"今日变动: {quote.get('netChange', 0):.2f} ({quote.get('netPercentChange', 0):.2f}%)")
        print(f"成交总量: {quote.get('totalVolume', 0):,}")
    else:
        print(f"❌ 查询行情失败: {resp.status_code}")

# ==========================================
# 主程序入口
# ==========================================
if __name__ == "__main__":
    # 1. 创建客户端
    schwab_client = get_schwab_client()

    # 2. 功能一：查看账户资产
    get_account_positions(schwab_client)

    # 3. 功能二：查看特定股票行情 (例如：NVDA 和 TSLA)
    get_market_quote(schwab_client, 'NVDA')
    get_market_quote(schwab_client, 'TSLA')