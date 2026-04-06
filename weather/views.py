# weather/views.py
import requests
from django.shortcuts import render
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env file properly
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

API_KEY = os.getenv("OPENWEATHER_API_KEY")


def home(request):
    weather_data = None
    forecast_data = []
    error = None
    weather_class = 'clear'


    if request.method == "POST":
        # Get city from dropdown OR manual input
        city_dropdown = request.POST.get("city")
        city_manual = request.POST.get("city_manual")
        city = city_manual if city_manual else city_dropdown

        if not API_KEY:
            error = "API key not loaded. Check your .env file."

        elif city:
            try:
                # -------- CURRENT WEATHER --------
                url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
                response = requests.get(url)
                data = response.json()


                if str(data.get("cod")) == "200":
                    weather_data = {
                        "city": data["name"],
                        "country": data["sys"]["country"],
                        "temp": round(data["main"]["temp"]),
                        "desc": data["weather"][0]["description"],
                        "icon": data["weather"][0]["icon"],
                        "humidity": data["main"]["humidity"],
                        "wind": data["wind"]["speed"],
                    }

                    # -------- WEATHER CLASS --------
                    main_weather = data["weather"][0]["main"].lower()

                    if main_weather in ['clouds', 'mist', 'fog']:
                        weather_class = "cloudy"
                    elif main_weather in ['rain', 'drizzle', 'thunderstorm']:
                        weather_class = "rain"
                    elif main_weather in ['snow']:
                        weather_class = "snow"
                    else:
                        weather_class = "clear"

                    # -------- FORECAST --------
                    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
                    forecast_resp = requests.get(forecast_url)
                    forecast_json = forecast_resp.json()


                    if forecast_json.get("cod") == "200":
                        for i in range(0, len(forecast_json['list']), 8):
                            day = forecast_json['list'][i]
                            forecast_data.append({
                                "date": day['dt_txt'].split(' ')[0],
                                "temp": round(day['main']['temp']),
                                "desc": day['weather'][0]['description'],
                                "icon": day['weather'][0]['icon']
                            })
                else:
                    error = "City not found! Use correct name like Mumbai,IN"

            except Exception as e:
                print("Error:", e)  # DEBUG
                error = "Something went wrong. Try again."

    return render(request, "index.html", {
        "weather": weather_data,
        "forecast": forecast_data,
        "error": error,
        "weather_class": weather_class
    })