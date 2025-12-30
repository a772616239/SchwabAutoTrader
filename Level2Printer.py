import asyncio
import json
import schwab
from schwab.auth import client_from_token_file
from schwab.streaming import StreamClient

# === 配置区域 ===
api_key = 'YOUR_APP_KEY'
app_secret = 'YOUR_APP_SECRET'
token_path = 'token.json'  # 你的 token 文件路径
# ================

class Level2Printer:
    """
    用于处理 Level 2 数据回调的类
    """
    def handle_l2_data(self, msg):
        # msg 是一个包含了推送数据的字典
        # 这里的结构非常复杂，通常包含 'service', 'timestamp', 'content' 等
        print("-" * 30)
        print("收到 Level 2 数据包:")
        
        # 简单的打印，实际应用中你需要解析 content 里的 bids/asks
        # content 里的 key: 0=Symbol, 1=Time, 2=Bid Price, 3=Ask Price 等 (需对照文档)
        print(json.dumps(msg, indent=2))
        print("-" * 30)

async def read_stream():
    # 1. 创建 HTTP Client (用于获取 Streamer Info 和 Token)
    # 确保 token.json 存在且有效
    client = client_from_token_file(token_path, api_key, app_secret)

    # 2. 获取 Account Hash (流媒体订阅需要用加密的 Account ID)
    account_details = client.get_account_numbers().json()
    # 通常取第一个账户的 hash value
    account_hash = account_details[0]['hashValue']
    print(f"使用账户 Hash: {account_hash}")

    # 3. 初始化 Stream Client
    stream_client = StreamClient(client, account_id=account_hash)

    # 4. 定义并绑定数据处理函数
    l2_handler = Level2Printer()
    
    # 绑定 NASDAQ Level 2 数据 (如果是纽交所股票，用 add_level_two_nyse_handler)
    # 或者使用通用的 add_book_handler (视库版本而定)
    stream_client.add_level_two_nasdaq_handler(l2_handler.handle_l2_data)
    
    # 也可以同时绑定 NYSE 的
    stream_client.add_level_two_nyse_handler(l2_handler.handle_l2_data)

    # 5. 登录流媒体服务
    await stream_client.login()
    print("登录流媒体服务成功")

    # 6. 设置服务质量 (QoS)
    # QoSLevel.EXPRESS = 最快速度 (无延迟聚合)
    await stream_client.quality_of_service(StreamClient.QoSLevel.EXPRESS)

    # 7. 订阅 Level 2 数据
    # 这里的 fields 指定我们需要哪些具体数据：
    # LevelTwoFields.QUOTES 通常包含价格、数量、做市商ID
    # 注意：Level 2 数据量巨大！
    symbols = ['AAPL', 'NVDA']
    
    print(f"开始订阅 {symbols} 的 Level 2 数据...")
    
    # 订阅 NASDAQ Book
    await stream_client.level_two_nasdaq_quotes(
        symbols,
        [stream_client.LevelTwoNasdaqFields.ALL] # 订阅所有可用字段
    )
    
    # 订阅 NYSE Book (如果是 listed 股票)
    await stream_client.level_two_nyse_quotes(
        symbols,
        [stream_client.LevelTwoNyseFields.ALL]
    )

    # 8. 保持连接并处理数据流
    while True:
        try:
            # 持续监听流
            await stream_client.handle_message()
        except Exception as e:
            print(f"连接断开或发生错误: {e}")
            break

if __name__ == '__main__':
    try:
        asyncio.run(read_stream())
    except KeyboardInterrupt:
        print("程序停止")