"""
weather_api: Retrieves current weather conditions and forecast data for any specified location
Tool Name: e_paper_weather_display
"""

import requests
import json
from datetime import datetime
def fetch_weather_data():
    location = input("Enter location (city name or city,country): ")
    api_key = input("Enter your OpenWeatherMap API key (get free at https://openweathermap.org/api): ")
    units = input("Enter units (metric for Celsius, imperial for Fahrenheit, or leave blank for Kelvin): ").strip()
    if not units:
        units = "standard"
    try:
        geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct"
        geocoding_params = {
            'q': location,
            'limit': 1,
            'appid': api_key
        }
        geo_response = requests.get(geocoding_url, params=geocoding_params)
        geo_response.raise_for_status()
        geo_data = geo_response.json()
        if not geo_data:
            raise Exception(f"Location '{location}' not found")
        lat = geo_data[0]['lat']
        lon = geo_data[0]['lon']
        location_name = geo_data[0]['name']
        country = geo_data[0].get('country', '')
        weather_url = "https://api.openweathermap.org/data/2.5/weather"
        weather_params = {
            'lat': lat,
            'lon': lon,
            'appid': api_key,
            'units': units
        }
        weather_response = requests.get(weather_url, params=weather_params)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
        forecast_response = requests.get(forecast_url, params=weather_params)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()
        unit_symbol = "°C" if units == "metric" else "°F" if units == "imperial" else "K"
        speed_unit = "m/s" if units == "metric" else "mph" if units == "imperial" else "m/s"
        result = {
            "timestamp": datetime.now().isoformat(),
            "query_location": location,
            "resolved_location": f"{location_name}, {country}" if country else location_name,
            "coordinates": {
                "latitude": lat,
                "longitude": lon
            },
            "current_weather": {
                "temperature": weather_data['main']['temp'],
                "feels_like": weather_data['main']['feels_like'],
                "temperature_min": weather_data['main']['temp_min'],
                "temperature_max": weather_data['main']['temp_max'],
                "pressure": weather_data['main']['pressure'],
                "humidity": weather_data['main']['humidity'],
                "visibility": weather_data.get('visibility', 'N/A'),
                "weather_condition": weather_data['weather'][0]['main'],
                "weather_description": weather_data['weather'][0]['description'],
                "weather_icon": weather_data['weather'][0]['icon'],
                "wind_speed": weather_data.get('wind', {}).get('speed', 'N/A'),
                "wind_direction": weather_data.get('wind', {}).get('deg', 'N/A'),
                "cloudiness": weather_data.get('clouds', {}).get('all', 'N/A'),
                "sunrise": datetime.fromtimestamp(weather_data['sys']['sunrise']).strftime('%H:%M:%S'),
                "sunset": datetime.fromtimestamp(weather_data['sys']['sunset']).strftime('%H:%M:%S')
            },
            "forecast": [],
            "units": {
                "temperature": unit_symbol,
                "speed": speed_unit,
                "pressure": "hPa",
                "humidity": "%",
                "visibility": "m"
            },
            "api_units_setting": units
        }
        for item in forecast_data['list'][:5]:
            forecast_item = {
                "datetime": datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d %H:%M:%S'),
                "temperature": item['main']['temp'],
                "weather_condition": item['weather'][0]['main'],
                "weather_description": item['weather'][0]['description'],
                "humidity": item['main']['humidity'],
                "wind_speed": item.get('wind', {}).get('speed', 'N/A')
            }
            result["forecast"].append(forecast_item)
        print("\n--- Current Weather Results ---")
        print(f"Location: {result['resolved_location']}")
        print(f"Coordinates: {result['coordinates']['latitude']}, {result['coordinates']['longitude']}")
        print(f"Temperature: {result['current_weather']['temperature']}{unit_symbol}")
        print(f"Feels Like: {result['current_weather']['feels_like']}{unit_symbol}")
        print(f"Condition: {result['current_weather']['weather_condition']} - {result['current_weather']['weather_description']}")
        print(f"Humidity: {result['current_weather']['humidity']}%")
        print(f"Pressure: {result['current_weather']['pressure']} hPa")
        print(f"Wind Speed: {result['current_weather']['wind_speed']} {speed_unit}")
        print(f"Cloudiness: {result['current_weather']['cloudiness']}%")
        print(f"Visibility: {result['current_weather']['visibility']} m")
        print(f"Sunrise: {result['current_weather']['sunrise']}")
        print(f"Sunset: {result['current_weather']['sunset']}")
        print(f"\n--- 5-Day Forecast ---")
        for i, forecast in enumerate(result['forecast'], 1):
            print(f"{i}. {forecast['datetime']}")
            print(f"   Temperature: {forecast['temperature']}{unit_symbol}")
            print(f"   Condition: {forecast['weather_condition']} - {forecast['weather_description']}")
            print(f"   Humidity: {forecast['humidity']}%")
        with open('tool_output.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print("\nData saved to tool_output.json")
        return result
    except requests.exceptions.RequestException as e:
        error_result = {"error": f"Network error: {str(e)}", "status": "failed", "timestamp": datetime.now().isoformat()}
        print(f"Network Error: {str(e)}")
        with open('tool_output.json', 'w', encoding='utf-8') as f:
            json.dump(error_result, f, ensure_ascii=False, indent=2)
        return error_result
    except KeyError as e:
        error_result = {"error": f"Data parsing error: Missing field {str(e)}", "status": "failed", "timestamp": datetime.now().isoformat()}
        print(f"Data Error: Missing field {str(e)}")
        with open('tool_output.json', 'w', encoding='utf-8') as f:
            json.dump(error_result, f, ensure_ascii=False, indent=2)
        return error_result
    except Exception as e:
        error_result = {"error": str(e), "status": "failed", "timestamp": datetime.now().isoformat()}
        print(f"Error: {str(e)}")
        with open('tool_output.json', 'w', encoding='utf-8') as f:
            json.dump(error_result, f, ensure_ascii=False, indent=2)
        return error_result
def main():
    fetch_weather_data()
if __name__ == "__main__":
    main()