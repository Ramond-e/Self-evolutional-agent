"""
stockkly_api: Fetches current or historical stock price data for any ticker symbol
Tool Name: stockkly_api
"""

import requests
import json
def fetch_stock_price(ticker, endpoint_type="current"):
    base_url = "https://stockkly-api.herokuapp.com/api"
    if endpoint_type == "current":
        url = f"{base_url}/prices/{ticker}"
    elif endpoint_type == "historical":
        url = f"{base_url}/pricesHistorical/{ticker}"
    else:
        raise ValueError("Invalid endpoint type. Use 'current' or 'historical'")
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch data: {str(e)}"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response"}
def display_stock_data(data, ticker, data_type):
    if "error" in data:
        print(f"Error: {data['error']}")
        return
    print(f"\n--- Stock Data for {ticker.upper()} ---")
    if data_type == "current":
        if isinstance(data, dict):
            for key, value in data.items():
                print(f"{key}: {value}")
        elif isinstance(data, list) and len(data) > 0:
            for key, value in data[0].items():
                print(f"{key}: {value}")
    elif data_type == "historical":
        if isinstance(data, list):
            print(f"Historical data (last {len(data)} entries):")
            for i, entry in enumerate(data[-10:]):
                print(f"Entry {i+1}: {entry}")
        else:
            print(f"Historical data: {data}")
def main():
    ticker = input("Enter stock ticker symbol: ").strip().upper()
    data_type = input("Enter data type (current/historical): ").strip().lower()
    if data_type not in ["current", "historical"]:
        print("Invalid data type. Using 'current' as default.")
        data_type = "current"
    print(f"Fetching {data_type} stock data for {ticker}...")
    stock_data = fetch_stock_price(ticker, data_type)
    display_stock_data(stock_data, ticker, data_type)
if __name__ == "__main__":
    main()