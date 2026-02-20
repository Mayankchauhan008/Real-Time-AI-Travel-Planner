import requests
from typing import Dict, List
from datetime import datetime, timedelta

class WeatherService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    def get_forecast(self, lat: float, lon: float, days: int = 5) -> List[Dict]:
        """Get weather forecast for location"""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if response.status_code == 200:
                # Group by day and get daily summary
                daily_forecasts = {}
                
                for item in data['list']:
                    date = datetime.fromtimestamp(item['dt']).date()
                    
                    if date not in daily_forecasts:
                        daily_forecasts[date] = {
                            'temps': [],
                            'descriptions': [],
                            'icons': []
                        }
                    
                    daily_forecasts[date]['temps'].append(item['main']['temp'])
                    daily_forecasts[date]['descriptions'].append(item['weather'][0]['description'])
                    daily_forecasts[date]['icons'].append(item['weather'][0]['icon'])
                
                # Create summary for each day
                forecasts = []
                for date, data in list(daily_forecasts.items())[:days]:
                    forecasts.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'day_name': date.strftime('%A'),
                        'temp_min': min(data['temps']),
                        'temp_max': max(data['temps']),
                        'temp_avg': sum(data['temps']) / len(data['temps']),
                        'description': max(set(data['descriptions']), 
                                         key=data['descriptions'].count),
                        'icon': max(set(data['icons']), 
                                   key=data['icons'].count)
                    })
                
                return forecasts
            
            return []
        except Exception as e:
            print(f"Weather error: {e}")
            return []
    
    def get_current_weather(self, lat: float, lon: float) -> Dict:
        """Get current weather"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if response.status_code == 200:
                return {
                    'temp': data['main']['temp'],
                    'feels_like': data['main']['feels_like'],
                    'description': data['weather'][0]['description'],
                    'icon': data['weather'][0]['icon'],
                    'humidity': data['main']['humidity'],
                    'wind_speed': data['wind']['speed']
                }
            
            return {}
        except Exception as e:
            print(f"Current weather error: {e}")
            return {}