#!/usr/bin/env python3
import json
from datetime import datetime

TRADES_PATH = 'trades.json'

def get_latest_trade():
    try:
        with open(TRADES_PATH, 'r', encoding='utf-8') as f:
            trades = json.load(f)
        
        if not trades:
            print("❌ 交易记录文件为空")
            return
        
        # 找到最新的交易记录
        latest_trade = None
        latest_time = None
        
        for trade in trades:
            try:
                trade_time = datetime.fromisoformat(trade['time'].replace('+0000', '+00:00'))
                
                if latest_time is None or trade_time > latest_time:
                    latest_time = trade_time
                    latest_trade = trade
            except Exception as e:
                print(f"❌ 解析时间失败: {e}")
                continue
        
        if latest_trade:
            print("✅ 最新交易记录:")
            print(json.dumps(latest_trade, ensure_ascii=False, indent=2))
        else:
            print("❌ 无法找到有效的交易记录")
            
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")

if __name__ == "__main__":
    get_latest_trade()
