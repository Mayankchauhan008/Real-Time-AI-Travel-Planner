import requests
import os
from typing import Dict, Optional, Tuple

class GeocodingService:
    def __init__(self, google_api_key: str, geoapify_api_key: str):
        self.google_key = google_api_key
        self.geoapify_key = geoapify_api_key
    
    def get_coordinates(self, location: str) -> Optional[Tuple[float, float]]:
        """Get latitude and longitude for a location"""
        try:
            # Using Geoapify for geocoding (better free tier)
            url = f"https://api.geoapify.com/v1/geocode/search"
            params = {
                'text': location,
                'apiKey': self.geoapify_key,
                'limit': 1
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get('features'):
                coords = data['features'][0]['geometry']['coordinates']
                return (coords[1], coords[0])  # lat, lon
            
            return None
        except Exception as e:
            return None
        except Exception as e:
            print(f"Geocoding error: {e}")
            from utils.mock_data import MockData
            return MockData.get_mock_coordinates(location)
    
    def get_place_details(self, location: str) -> Dict:
        """Get detailed information about a place"""
        try:
            url = f"https://api.geoapify.com/v1/geocode/search"
            params = {
                'text': location,
                'apiKey': self.geoapify_key,
                'limit': 1
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get('features'):
                props = data['features'][0]['properties']
                return {
                    'name': props.get('formatted'),
                    'city': props.get('city'),
                    'country': props.get('country'),
                    'lat': props.get('lat'),
                    'lon': props.get('lon')
                }
            
            return {}
        except Exception as e:
            return {}
        except Exception as e:
            print(f"Place details error: {e}")
            # Fallback for place details
            from utils.mock_data import MockData
            lat, lon = MockData.get_mock_coordinates(location)
            return {
                'name': location.title(),
                'city': location.title(),
                'country': "Demo Country",
                'lat': lat,
                'lon': lon
            }