"""
stockkly_api: Fetches current or historical stock price data for any ticker symbol
Tool Name: stockkly_api
"""

import requests
import json
from datetime import datetime

def fetch_stock_price_yfinance(ticker):
    """Fetch stock data using Yahoo Finance API (no key required)"""
    # Using query1.finance.yahoo.com API
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if 'chart' in data and 'result' in data['chart'] and len(data['chart']['result']) > 0:
            result = data['chart']['result'][0]
            meta = result.get('meta', {})
            
            # Extract current price and other data
            current_price = meta.get('regularMarketPrice', 'N/A')
            previous_close = meta.get('previousClose', 'N/A')
            
            # Calculate change
            if current_price != 'N/A' and previous_close != 'N/A':
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100
            else:
                change = 'N/A'
                change_percent = 'N/A'
            
            return {
                'symbol': ticker.upper(),
                'price': current_price,
                'previousClose': previous_close,
                'change': change,
                'changePercent': change_percent,
                'currency': meta.get('currency', 'USD'),
                'exchangeName': meta.get('exchangeName', 'N/A'),
                'regularMarketTime': datetime.fromtimestamp(meta.get('regularMarketTime', 0)).strftime('%Y-%m-%d %H:%M:%S') if meta.get('regularMarketTime') else 'N/A'
            }
        else:
            return {"error": f"No data found for ticker {ticker}"}
            
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch data: {str(e)}"}
    except Exception as e:
        return {"error": f"Error processing data: {str(e)}"}

def display_stock_data(data, ticker):
    """Display stock data in a formatted way"""
    if "error" in data:
        print(f"Error: {data['error']}")
        return
    
    print(f"\n--- 股票数据 {ticker.upper()} ---")
    print(f"股票代码: {data.get('symbol', 'N/A')}")
    print(f"当前价格: ${data.get('price', 'N/A')}")
    print(f"前收盘价: ${data.get('previousClose', 'N/A')}")
    
    change = data.get('change', 'N/A')
    change_percent = data.get('changePercent', 'N/A')
    
    if change != 'N/A' and change_percent != 'N/A':
        # Format change with + or - sign
        change_str = f"+${change:.2f}" if change >= 0 else f"-${abs(change):.2f}"
        percent_str = f"+{change_percent:.2f}%" if change_percent >= 0 else f"{change_percent:.2f}%"
        print(f"涨跌额: {change_str}")
        print(f"涨跌幅: {percent_str}")
    
    print(f"货币: {data.get('currency', 'N/A')}")
    print(f"交易所: {data.get('exchangeName', 'N/A')}")
    print(f"更新时间: {data.get('regularMarketTime', 'N/A')}")
    
    # Save to file for other tools
    with open('tool_output.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return data

def main():
    ticker = input("Enter stock ticker symbol (e.g., AAPL, NVDA, TSLA): ").strip().upper()
    
    print(f"\nFetching current stock data for {ticker}...")
    stock_data = fetch_stock_price_yfinance(ticker)
    display_stock_data(stock_data, ticker)

if __name__ == "__main__":
    main()