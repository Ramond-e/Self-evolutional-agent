"""
stockkly_api: Fetches current or historical stock price data for any ticker symbol
Tool Name: stockkly_api
"""

import requests
import json
from datetime import datetime
import os

def fetch_stock_price_alphavantage(ticker, api_key):
    """Fetch stock data using Alpha Vantage API"""
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={api_key}"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Check for API limit error
        if "Note" in data or "Information" in data:
            return {"error": "API调用限制：免费账户每分钟5次，每天500次请求。请稍后再试。"}
        
        if "Global Quote" in data and data["Global Quote"]:
            quote = data["Global Quote"]
            
            # Check if we got valid data
            if not quote.get('05. price'):
                return {"error": f"未找到股票代码 {ticker} 的数据"}
            
            price = float(quote.get('05. price', 0))
            prev_close = float(quote.get('08. previous close', 0))
            change = float(quote.get('09. change', 0))
            
            return {
                'symbol': quote.get('01. symbol', ticker.upper()),
                'price': price,
                'open': float(quote.get('02. open', 0)),
                'high': float(quote.get('03. high', 0)),
                'low': float(quote.get('04. low', 0)),
                'volume': quote.get('06. volume', 'N/A'),
                'previousClose': prev_close,
                'change': change,
                'changePercent': quote.get('10. change percent', 'N/A'),
                'latestTradingDay': quote.get('07. latest trading day', 'N/A'),
                'source': 'Alpha Vantage API'
            }
        else:
            return {"error": f"未找到股票代码 {ticker} 的数据"}
            
    except Exception as e:
        return {"error": f"获取数据失败: {str(e)}"}

def fetch_stock_price_demo(ticker):
    """使用demo key获取股票数据（仅支持特定股票）"""
    demo_symbols = ['IBM', 'MSFT', 'AAPL', 'GOOGL', 'AMZN']
    
    if ticker.upper() not in demo_symbols:
        return {
            'symbol': ticker.upper(),
            'demo_mode': True,
            'message': f'Demo模式仅支持: {", ".join(demo_symbols)}',
            'instruction': '要查询其他股票，请使用您自己的API密钥'
        }
    
    return fetch_stock_price_alphavantage(ticker, "demo")

def get_or_request_api_key():
    """获取或请求API密钥"""
    # 首先检查环境变量
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    
    if api_key:
        print("✅ 使用环境变量中的 Alpha Vantage API 密钥")
        return api_key
    
    # 检查.env文件
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('ALPHA_VANTAGE_API_KEY='):
                    api_key = line.strip().split('=')[1]
                    if api_key:
                        print("✅ 使用 .env 文件中的 Alpha Vantage API 密钥")
                        return api_key
    
    # 如果没有找到，询问用户
    print("\n📊 股票价格查询需要 Alpha Vantage API 密钥")
    print("🆓 免费注册获取API密钥: https://www.alphavantage.co/support/#api-key")
    print("💡 提示: 注册只需邮箱，立即获得密钥，每天500次免费查询")
    
    choice = input("\n选择操作:\n1. 输入我的API密钥\n2. 使用Demo模式（仅支持部分股票）\n请选择 (1/2): ").strip()
    
    if choice == '1':
        api_key = input("请输入您的 Alpha Vantage API 密钥: ").strip()
        if api_key:
            # 可选：保存到.env文件
            save_choice = input("\n是否保存密钥以便下次使用？(y/n): ").strip().lower()
            if save_choice == 'y':
                with open('.env', 'a') as f:
                    f.write(f"\n# Alpha Vantage API Key for stock data\nALPHA_VANTAGE_API_KEY={api_key}\n")
                print("✅ API密钥已保存到 .env 文件")
            return api_key
    
    # 默认返回demo
    return "demo"

def fetch_stock_price(ticker):
    """获取股票价格的主函数"""
    api_key = get_or_request_api_key()
    
    if api_key == "demo":
        print("\n📌 使用Demo模式...")
        return fetch_stock_price_demo(ticker)
    else:
        print(f"\n📈 正在查询 {ticker} 的实时数据...")
        return fetch_stock_price_alphavantage(ticker, api_key)

def display_stock_data(data, ticker):
    """Display stock data in a formatted way"""
    if "error" in data:
        print(f"\n❌ 错误: {data['error']}")
        return data
    
    if 'demo_mode' in data:
        print(f"\n⚠️ Demo模式提示:")
        print(f"💡 {data['message']}")
        print(f"📝 {data['instruction']}")
        return data
    
    print(f"\n📊 {ticker.upper()} 股票数据")
    print("=" * 40)
    
    # Basic info
    print(f"股票代码: {data.get('symbol', ticker.upper())}")
    
    # Price info
    price = data.get('price', 0)
    if price:
        print(f"当前价格: ${price:.2f}")
    
    # Previous close and change
    if 'previousClose' in data and data['previousClose']:
        prev_close = data['previousClose']
        print(f"前收盘价: ${prev_close:.2f}")
        
        if 'change' in data:
            change = data['change']
            change_str = f"+${change:.2f}" if change >= 0 else f"-${abs(change):.2f}"
            print(f"涨跌额: {change_str}")
        
        if 'changePercent' in data:
            change_percent = data['changePercent']
            print(f"涨跌幅: {change_percent}")
    
    # Additional info
    if 'open' in data and data['open']:
        print(f"今日开盘: ${data['open']:.2f}")
    
    if 'high' in data and data['high']:
        print(f"今日最高: ${data['high']:.2f}")
        
    if 'low' in data and data['low']:
        print(f"今日最低: ${data['low']:.2f}")
    
    if 'volume' in data and data['volume'] != 'N/A':
        print(f"成交量: {data['volume']}")
        
    if 'latestTradingDay' in data:
        print(f"最新交易日: {data['latestTradingDay']}")
    
    if 'source' in data:
        print(f"\n数据来源: {data['source']}")
    
    print("=" * 40)
    
    # Save to file for other tools
    with open('tool_output.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return data

def main():
    print("🎯 股票价格查询工具")
    print("=" * 40)
    
    ticker = input("请输入股票代码 (例如: NVDA, TSLA, AAPL): ").strip().upper()
    
    if not ticker:
        print("❌ 股票代码不能为空")
        return
    
    stock_data = fetch_stock_price(ticker)
    display_stock_data(stock_data, ticker)

if __name__ == "__main__":
    main()