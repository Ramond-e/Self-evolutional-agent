"""
weather_api: Retrieves current weather conditions for Shanghai including temperature and humidity
Tool Name: e_paper_weather_display
"""

import requests
def main():
    api_key = input("Enter your OpenWeatherMap API key: ")
    city = "Shanghai"
    units = "metric"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units={units}&lang=zh"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        description = data['weather'][0]['description']
        wind_speed = data['wind']['speed']
        print("上海今天的天气:")
        print(f"温度: {temp}°C")
        print(f"体感温度: {feels_like}°C")
        print(f"湿度: {humidity}%")
        print(f"天气描述: {description}")
        print(f"风速: {wind_speed} m/s")
    except requests.exceptions.RequestException as e:
        print(f"获取天气数据时出错: {e}")
    except KeyError as e:
        print(f"解析天气数据时出错: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")
if __name__ == "__main__":
    main()