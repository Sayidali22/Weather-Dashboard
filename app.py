from flask import Flask, render_template, request, jsonify
import requests
import time

app = Flask(__name__)

# Simple in-memory cache
cache = {}
CACHE_DURATION = 600  # 10 minutes in seconds

# Your API key will go here
API_KEY = "5141fe72bfbd756a2a5a1ff2d6c9cc9a"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/weather', methods=['POST'])
def get_weather():
    city = request.json.get('city', '')
    
    if not city:
        return jsonify({'error': 'Please enter a city name'}), 400
    
    # Check cache first
    current_time = time.time()
    if city in cache:
        cached_data, timestamp = cache[city]
        if current_time - timestamp < CACHE_DURATION:
            print(f"Using cached data for {city}")
            return jsonify(cached_data)
    
    # Make API call if not in cache
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=imperial"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            weather_data = {
                'city': data['name'],
                'temperature': round(data['main']['temp']),
                'description': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'wind_speed': round(data['wind']['speed'])
            }
            
            # Store in cache
            cache[city] = (weather_data, current_time)
            return jsonify(weather_data)
        else:
            return jsonify({'error': 'City not found'}), 404
            
    except Exception as e:
        return jsonify({'error': 'Failed to fetch weather data'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)