from django.shortcuts import render
import requests
# Create your views here.
from datetime import datetime
API_KEY = '2f2881a5959446bc3ac5562dcebab6cd'

def convert_unix_to_time(unix_timestamp):
    return datetime.fromtimestamp(unix_timestamp).strftime('%I:%M %p')



def get_weather_data(city):
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(weather_url)
    return response.json()


def weather_view(request):
    city = request.GET.get('city', 'Hyderabad')  # default city
    data = get_weather_data(city)
    

    context = {}

    if data.get('cod') == 200:
        

        context['Weather'] = {
            'city': data['name'],
            'temparature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'visibility': data['visibility'] / 1000,
            'description': data['weather'][0]['description'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
            'sunrise': convert_unix_to_time(data['sys']['sunrise']),
            'sunset': convert_unix_to_time(data['sys']['sunset']),
        }
        
        lat = data['coord']['lat']
        lon = data['coord']['lon']
    
        aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
        aqi_response = requests.get(aqi_url)
        aqi_data = aqi_response.json()
        if 'list' in aqi_data and len(aqi_data['list']) > 0:
            pollution = aqi_data['list'][0]['components']
            context['AirQuality'] = {
                'co': pollution.get('co'),
                'so2': pollution.get('so2'),
                'o3': pollution.get('o3'),
                'no2': pollution.get('no2'),
            }
        
        # 📆 5-Day Forecast Data
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&appid={API_KEY}"
        forecast_response = requests.get(forecast_url)
        forecast_data = forecast_response.json()

        next_days = []

        if 'list' in forecast_data:
            from datetime import datetime
            added_dates = set()
            for entry in forecast_data['list']:
                date_txt = entry['dt_txt']
                date_obj = datetime.strptime(date_txt, "%Y-%m-%d %H:%M:%S")

                if date_obj.hour == 12 and date_obj.date() not in added_dates:
                    next_days.append({
                        'date': date_obj.strftime('%d-%m-%Y'),
                        'day': date_obj.strftime('%A'),
                        'temp': entry['main']['temp'],
                        'icon': entry['weather'][0]['icon']
                    })
                    added_dates.add(date_obj.date())

                if len(next_days) == 5:
                    break

            context['Forecast'] = next_days
        
        today_date = datetime.now().date()

# Define desired hours
        desired_hours = [6, 9, 12, 15, 18, 21]
        today_forecast = []

        for entry in forecast_data['list']:
            dt_txt = entry['dt_txt']  # e.g., "2025-04-17 06:00:00"
            date_obj = datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S")
    
        if date_obj.date() == today_date and date_obj.hour in desired_hours:
            today_forecast.append({
                'time': date_obj.strftime('%I:%M %p'),
                'temp': entry['main']['temp'],
                'icon': entry['weather'][0]['icon']
                })

            context['TodayForecast'] = today_forecast


    else:
        context['Weather'] = {'city': 'Not Found', 'temparature': 0, 'description': 'N/A'}

    return render(request,'index.html',context)