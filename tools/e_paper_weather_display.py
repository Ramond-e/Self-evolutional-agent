"""
weather_api: Retrieves current weather conditions for a given city using OpenWeatherMap API
Tool Name: e_paper_weather_display
"""

import requests
import json
def get_weather(city, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric',
        'lang': 'zh_cn'
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    if response.status_code == 200:
        weather_desc = data['weather'][0]['description']
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        pressure = data['main']['pressure']
        wind_speed = data['wind']['speed']
        print(f"城市: {city}")
        print(f"天气状况: {weather_desc}")
        print(f"当前温度: {temp}°C")
        print(f"体感温度: {feels_like}°C")
        print(f"湿度: {humidity}%")
        print(f"气压: {pressure} hPa")
        print(f"风速: {wind_speed} m/s")
    else:
        print(f"获取天气信息失败: {data.get('message', '未知错误')}")
def main():
    api_key = input("请输入您的OpenWeatherMap API密钥: ")
    city = input("请输入城市名称 (例如: Shanghai): ")
    get_weather(city, api_key)
if __name__ == "__main__":
    main()