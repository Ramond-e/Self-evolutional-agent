"""
finnhub_python: Retrieves comprehensive stock data including quotes, company profiles, financials, and news
Tool Name: finnhub-python
"""

import finnhub
import json
import datetime
import time
def fetch_data():
    ticker = input("Enter stock ticker symbol (e.g., AAPL, TSLA, MSFT): ").upper().strip()
    api_key = input("Enter your Finnhub API key (get free at https://finnhub.io/): ").strip()
    data_type = input("Select data type (1: Current Quote, 2: Company Profile, 3: Basic Financials, 4: Recent News): ").strip()
    try:
        finnhub_client = finnhub.Client(api_key=api_key)
        result = {
            "ticker": ticker,
            "timestamp": datetime.datetime.now().isoformat(),
            "data_type": data_type
        }
        if data_type == "1":
            quote_data = finnhub_client.quote(ticker)
            result.update({
                "current_price": quote_data.get('c'),
                "change": quote_data.get('d'),
                "percent_change": quote_data.get('dp'),
                "high_price": quote_data.get('h'),
                "low_price": quote_data.get('l'),
                "open_price": quote_data.get('o'),
                "previous_close": quote_data.get('pc'),
                "raw_quote_data": quote_data
            })
        elif data_type == "2":
            profile_data = finnhub_client.company_profile2(symbol=ticker)
            result.update({
                "company_name": profile_data.get('name'),
                "industry": profile_data.get('finnhubIndustry'),
                "country": profile_data.get('country'),
                "currency": profile_data.get('currency'),
                "market_cap": profile_data.get('marketCapitalization'),
                "share_outstanding": profile_data.get('shareOutstanding'),
                "website": profile_data.get('weburl'),
                "logo": profile_data.get('logo'),
                "raw_profile_data": profile_data
            })
        elif data_type == "3":
            financials_data = finnhub_client.company_basic_financials(ticker, 'all')
            result.update({
                "annual_data": financials_data.get('annual'),
                "quarterly_data": financials_data.get('quarterly'),
                "metrics": financials_data.get('metric'),
                "raw_financials_data": financials_data
            })
        elif data_type == "4":
            current_date = datetime.datetime.now()
            one_week_ago = current_date - datetime.timedelta(days=7)
            news_data = finnhub_client.company_news(ticker,
                                                    _from=one_week_ago.strftime('%Y-%m-%d'),
                                                    to=current_date.strftime('%Y-%m-%d'))
            result.update({
                "news_count": len(news_data),
                "recent_news": news_data[:5] if len(news_data) > 5 else news_data,
                "raw_news_data": news_data
            })
        print("\n--- Stock Data Results ---")
        print(f"Ticker: {result.get('ticker')}")
        print(f"Data Type: {result.get('data_type')}")
        print(f"Timestamp: {result.get('timestamp')}")
        if data_type == "1":
            print(f"Current Price: ${result.get('current_price', 'N/A')}")
            print(f"Change: ${result.get('change', 'N/A')}")
            print(f"Percent Change: {result.get('percent_change', 'N/A')}%")
            print(f"Day High: ${result.get('high_price', 'N/A')}")
            print(f"Day Low: ${result.get('low_price', 'N/A')}")
            print(f"Open Price: ${result.get('open_price', 'N/A')}")
            print(f"Previous Close: ${result.get('previous_close', 'N/A')}")
        elif data_type == "2":
            print(f"Company Name: {result.get('company_name', 'N/A')}")
            print(f"Industry: {result.get('industry', 'N/A')}")
            print(f"Country: {result.get('country', 'N/A')}")
            print(f"Currency: {result.get('currency', 'N/A')}")
            print(f"Market Cap: ${result.get('market_cap', 'N/A')} million")
            print(f"Website: {result.get('website', 'N/A')}")
        elif data_type == "3":
            print("Financial Metrics:")
            metrics = result.get('metrics', {})
            for key, value in list(metrics.items())[:10]:
                print(f"  {key}: {value}")
        elif data_type == "4":
            print(f"Recent News Count: {result.get('news_count', 0)}")
            recent_news = result.get('recent_news', [])
            for i, news in enumerate(recent_news[:3], 1):
                print(f"\nNews {i}:")
                print(f"  Headline: {news.get('headline', 'N/A')}")
                print(f"  Source: {news.get('source', 'N/A')}")
                print(f"  Date: {datetime.datetime.fromtimestamp(news.get('datetime', 0)).strftime('%Y-%m-%d %H:%M')}")
        with open('tool_output.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print("\nData saved to tool_output.json")
        return result
    except Exception as e:
        print(f"Error: {str(e)}")
        error_result = {
            "error": str(e),
            "status": "failed",
            "ticker": ticker if 'ticker' in locals() else "unknown",
            "timestamp": datetime.datetime.now().isoformat()
        }
        with open('tool_output.json', 'w', encoding='utf-8') as f:
            json.dump(error_result, f, ensure_ascii=False, indent=2)
        return error_result
def main():
    fetch_data()
if __name__ == "__main__":
    main()