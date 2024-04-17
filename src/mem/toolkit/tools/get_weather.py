import requests


async def get_weather_data(is_forecast, latitude, longitude):
    url = f"https://api.weather.gov/points/{latitude},{longitude}"
    response = requests.get(url)
    if response.status_code == 200:
        forecast_url = response.json().get("properties").get("forecast")
        if forecast_url:
            data = requests.get(forecast_url)
            if data.status_code == 200:
                forecast = data.json()
                today = forecast["properties"]["periods"][0]
                todays_weather = {
                    "temperature": today.get("temperature"),
                    "detailedForecast": today.get("detailedForecast"),
                }
                seven_day_forecast = []
                for weather in forecast["properties"]["periods"]:
                    if weather["isDaytime"]:
                        daily_forecast = {
                            "day_name": weather["name"],
                            "temperature": weather["temperature"],
                            "shortForecast": weather["shortForecast"],
                        }
                        seven_day_forecast.append(daily_forecast)
                print(is_forecast)
                if str(is_forecast).lower() == "true" or is_forecast:
                    return {"seven_day_forecast": seven_day_forecast}
                else:
                    return {
                        "todays_weather": todays_weather,
                    }

            return {"error": "Could not get forecast data"}


if __name__ == "__main__":
    print(
        get_weather_data(is_forecast="true", latitude="37.7749", longitude="-122.4194")
    )
