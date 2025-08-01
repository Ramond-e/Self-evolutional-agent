"""
jarvis: Fetches current weather data including temperature, humidity, and conditions for cities
Tool Name: J.A.R.V.I.S
"""

import requests
import json
def main():
    api_key = input("Enter your weather API key: ")
    city = input("Enter city name (or press Enter for Beijing): ")
    if not city:
        city = "Beijing"
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "lang": "zh"
    }
    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        if response.status_code == 200:
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            description = data["weather"][0]["description"]
            wind_speed = data["wind"]["speed"]
            print(f"\n{city}今天的天气情况:")
            print(f"温度: {temp}°C")
            print(f"体感温度: {feels_like}°C")
            print(f"天气状况: {description}")
            print(f"湿度: {humidity}%")
            print(f"风速: {wind_speed} m/s")
        else:
            print(f"获取天气信息失败: {data.get('message', '未知错误')}")
    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {e}")
    except KeyError as e:
        print(f"数据解析错误: {e}")
    except Exception as e:
        print(f"发生错误: {e}")
if __name__ == "__main__":
    main()