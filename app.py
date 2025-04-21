from flask import Flask, render_template, request
import requests
from datetime import datetime
import pytz

app = Flask(__name__)

API_KEY = "8c1a5be7024c0eba1ebdeae533509c60"  

@app.route('/', methods=['GET', 'POST'])
def index():
    city = request.form.get('city', '')
    weather_data = None
    error_message = None
    
    if city:
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            response = requests.get(url)
            response.raise_for_status()  
            
            data = response.json()
            
            timezone_offset = data['timezone']  
            local_time = datetime.utcnow().replace(tzinfo=pytz.utc)
            local_time = local_time.astimezone(pytz.FixedOffset(timezone_offset//60))
            
            hour = local_time.hour
            is_day = 6 <= hour < 18
            
            weather_id = data['weather'][0]['id']
            is_sunny = weather_id == 800  
    
            weather_data = {
                'city': data['name'],
                'country': data['sys']['country'],
                'temp': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'humidity': data['main']['humidity'],
                'wind': round(data['wind']['speed'] * 3.6, 1),  
                'weather': data['weather'][0]['main'],
                'description': data['weather'][0]['description'].capitalize(),
                'icon': data['weather'][0]['icon'],
                'is_day': is_day,
                'is_sunny': is_sunny,
                'time_of_day': 'Day' if is_day else 'Night'
            }
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                error_message = f"City '{city}' not found. Please check the spelling."
            else:
                error_message = f"Error fetching weather data: {e}"
        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"
    
    return render_template('index.html', city=city, weather_data=weather_data, error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)
