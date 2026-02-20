import googlemaps
import requests
from typing import List, Dict
from datetime import datetime
from utils.mock_data import MockData

class PlacesService:
    def __init__(self, google_api_key: str):
        self.gmaps = googlemaps.Client(key=google_api_key)
        self.api_key = google_api_key
    
    def search_hotels(self, location: str, lat: float, lon: float, 
                     budget: str = "moderate", radius: int = 5000) -> List[Dict]:
        """Search for real hotels near location"""
        try:
            # Determine price level based on budget
            price_map = {
                "Budget ($50-100/day)": [0, 1, 2],
                "Moderate ($100-300/day)": [2, 3],
                "Luxury ($300-500/day)": [3, 4],
                "Ultra Luxury ($500+/day)": [4]
            }
            
            price_levels = price_map.get(budget, [2, 3])
            
            # Search for hotels
            try:
                places_result = self.gmaps.places_nearby(
                    location=(lat, lon),
                    radius=radius,
                    type='lodging',
                    open_now=False
                )
            except Exception:
                places_result = {}
            
            hotels = []
            if places_result.get('results'):
                for place in places_result.get('results', [])[:10]:
                    price_level = place.get('price_level', 2)
                    
                    # Filter by budget
                    if price_level in price_levels:
                        # Get place details for more info
                        try:
                            details = self.gmaps.place(place['place_id'], 
                                                      fields=['formatted_phone_number', 
                                                             'website', 'opening_hours'])
                        except:
                            details = {'result': {}}

                        hotel_info = {
                            'name': place['name'],
                            'address': place.get('vicinity', 'Address not available'),
                            'rating': place.get('rating', 0),
                            'total_ratings': place.get('user_ratings_total', 0),
                            'price_level': price_level,
                            'lat': place['geometry']['location']['lat'],
                            'lon': place['geometry']['location']['lng'],
                            'place_id': place['place_id'],
                            'photo_reference': place.get('photos', [{}])[0].get('photo_reference') if place.get('photos') else None,
                            'website': details['result'].get('website', 'N/A'),
                            'phone': details['result'].get('formatted_phone_number', 'N/A'),
                            'estimated_price': self._estimate_price(price_level)
                        }
                        hotels.append(hotel_info)
            
            # Fallback to mock data if no hotels found
            if not hotels:
                print("Using mock hotels")
                hotels = MockData.get_hotels(location, lat, lon)

            # Sort by rating
            hotels.sort(key=lambda x: (x.get('rating', 0), x.get('total_ratings', 0)), reverse=True)
            return hotels[:5]  # Return top 5
            
        except Exception as e:
            print(f"Hotel search error: {e}")
            return MockData.get_hotels(location, lat, lon)
    
    def search_restaurants(self, lat: float, lon: float, 
                          cuisine_type: str = None, radius: int = 2000) -> List[Dict]:
        """Search for restaurants near location"""
        try:
            params = {
                'location': (lat, lon),
                'radius': radius,
                'type': 'restaurant',
                'open_now': False
            }
            
            if cuisine_type:
                params['keyword'] = cuisine_type
            
            try:
                places_result = self.gmaps.places_nearby(**params)
            except Exception:
                places_result = {}
            
            restaurants = []
            if places_result.get('results'):
                for place in places_result.get('results', [])[:20]:
                    rest_info = {
                        'name': place['name'],
                        'address': place.get('vicinity', 'N/A'),
                        'rating': place.get('rating', 0),
                        'price_level': place.get('price_level', 2),
                        'lat': place['geometry']['location']['lat'],
                        'lon': place['geometry']['location']['lng'],
                        'place_id': place['place_id'],
                        'types': place.get('types', []),
                        'estimated_cost': self._estimate_meal_cost(place.get('price_level', 2))
                    }
                    restaurants.append(rest_info)
            
            # Fallback to mock data
            if not restaurants:
                print("Using mock restaurants")
                restaurants = MockData.get_restaurants("City", lat, lon)

            # Sort by rating
            restaurants.sort(key=lambda x: x.get('rating', 0), reverse=True)
            return restaurants[:10]
            
        except Exception as e:
            print(f"Restaurant search error: {e}")
            return MockData.get_restaurants("City", lat, lon)
    
    def search_attractions(self, lat: float, lon: float, 
                          interest: str = None, radius: int = 5000) -> List[Dict]:
        """Search for tourist attractions"""
        try:
            # Map interests to search types
            type_map = {
                "Culture & History": "museum",
                "Nature": "park",
                "Shopping": "shopping_mall",
                "Adventure": "amusement_park",
                "Nightlife": "night_club",
                "Relaxation": "spa"
            }
            
            search_type = type_map.get(interest, "tourist_attraction")
            
            try:
                places_result = self.gmaps.places_nearby(
                    location=(lat, lon),
                    radius=radius,
                    type=search_type
                )
            except Exception:
                places_result = {}
            
            attractions = []
            if places_result.get('results'):
                for place in places_result.get('results', [])[:15]:
                    attr_info = {
                        'name': place['name'],
                        'address': place.get('vicinity', 'N/A'),
                        'rating': place.get('rating', 0),
                        'lat': place['geometry']['location']['lat'],
                        'lon': place['geometry']['location']['lng'],
                        'place_id': place['place_id'],
                        'types': place.get('types', []),
                        'photos': place.get('photos', [])
                    }
                    attractions.append(attr_info)
            
            # Fallback to mock data
            if not attractions:
                print("Using mock attractions")
                attractions = MockData.get_attractions("City", lat, lon)

            attractions.sort(key=lambda x: x.get('rating', 0), reverse=True)
            return attractions[:8]
            
        except Exception as e:
            print(f"Attractions search error: {e}")
            return MockData.get_attractions("City", lat, lon)
    
    def get_photo_url(self, photo_reference: str, max_width: int = 400) -> str:
        """Get photo URL from photo reference"""
        if not photo_reference:
            return None
        return f"https://maps.googleapis.com/maps/api/place/photo?maxwidth={max_width}&photo_reference={photo_reference}&key={self.api_key}"
    
    def _estimate_price(self, price_level: int) -> str:
        """Estimate hotel price per night based on price level"""
        price_ranges = {
            0: "$30-50",
            1: "$50-80",
            2: "$80-150",
            3: "$150-300",
            4: "$300+"
        }
        return price_ranges.get(price_level, "$80-150")
    
    def _estimate_meal_cost(self, price_level: int) -> str:
        """Estimate meal cost based on price level"""
        meal_costs = {
            0: "$5-10",
            1: "$10-20",
            2: "$20-40",
            3: "$40-80",
            4: "$80+"
        }
        return meal_costs.get(price_level, "$20-40")
    
    def calculate_distance(self, origin_lat: float, origin_lon: float,
                          dest_lat: float, dest_lon: float) -> Dict:
        """Calculate distance and travel time between two points"""
        try:
            result = self.gmaps.distance_matrix(
                origins=(origin_lat, origin_lon),
                destinations=(dest_lat, dest_lon),
                mode="walking"
            )
            
            if result['rows'][0]['elements'][0]['status'] == 'OK':
                return {
                    'distance': result['rows'][0]['elements'][0]['distance']['text'],
                    'duration': result['rows'][0]['elements'][0]['duration']['text']
                }
            return {'distance': 'N/A', 'duration': 'N/A'}
        except:
            return {'distance': 'N/A', 'duration': 'N/A'}