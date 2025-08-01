"""
stockkly_api: Fetches real-time NVIDIA stock price data including current price and changes
Tool Name: stockkly_api
"""

import requests
import json
def main():
    print("获取英伟达(NVDA)股价信息")
    try:
        response = requests.get("https://stockkly-api.onrender.com/api/prices/NVDA")
        if response.status_code == 200:
            data = response.json()
            print(f"股票代码: {data.get('ticker', 'N/A')}")
            print(f"当前价格: ${data.get('price', 'N/A')}")
            print(f"涨跌额: ${data.get('change', 'N/A')}")
            print(f"涨跌幅: {data.get('changePercent', 'N/A')}%")
            print(f"最后更新时间: {data.get('lastUpdated', 'N/A')}")
        else:
            print(f"获取数据失败，状态码: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
    except json.JSONDecodeError:
        print("数据解析错误")
    except Exception as e:
        print(f"发生错误: {e}")
if __name__ == "__main__":
    main()