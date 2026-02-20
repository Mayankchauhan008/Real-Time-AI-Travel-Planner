
import random
from typing import List, Dict

class MockData:
    @staticmethod
    def get_mock_coordinates(city_name: str) -> tuple:
        """Return fallback coordinates for popular cities or a default one"""
        cities = {
            "paris": (48.8566, 2.3522),
            "london": (51.5074, -0.1278),
            "new york": (40.7128, -74.0060),
            "tokyo": (35.6762, 139.6503),
            "dubai": (25.2048, 55.2708),
            "singapore": (1.3521, 103.8198),
            "mumbai": (19.0760, 72.8777),
            "gujarat": (23.2156, 72.6369),  # Gandhinagar
            "ahmedabad": (23.0225, 72.5714),
            "delhi": (28.6139, 77.2090),
            "bangalore": (12.9716, 77.5946),
        }
        return cities.get(city_name.lower(), (48.8566, 2.3522))  # Default to Paris

    @staticmethod
    def _add_random_offset(lat: float, lon: float) -> tuple:
        """Add small random offset to coordinates to spread pins on map"""
        # Roughly 111km per degree. 0.01 degree is ~1.1km
        lat_offset = random.uniform(-0.02, 0.02)
        lon_offset = random.uniform(-0.02, 0.02)
        return lat + lat_offset, lon + lon_offset

    @staticmethod
    def get_hotels(city_name: str, lat: float, lon: float) -> List[Dict]:
        """Generate mock hotels around a location"""
        prefixes = ["Grand", "Royal", "City Center", "Luxury", "Boutique", "Seaside", "Heritage"]
        suffixes = ["Hotel", "Resort", "Suites", "Inn", "Palace", "Stay"]
        
        hotels = []
        for i in range(5):
            name = f"{random.choice(prefixes)} {city_name.capitalize()} {random.choice(suffixes)}"
            h_lat, h_lon = MockData._add_random_offset(lat, lon)
            
            hotels.append({
                'name': name,
                'address': f"{random.randint(1, 999)} {random.choice(['Main St', 'Park Ave', 'Broadway', 'Market Rd'])}, {city_name}",
                'rating': round(random.uniform(3.8, 5.0), 1),
                'total_ratings': random.randint(50, 1000),
                'price_level': random.randint(2, 4),
                'lat': h_lat,
                'lon': h_lon,
                'place_id': f"mock_hotel_{i}",
                'photo_reference': None,
                'website': 'https://example.com',
                'phone': f"+1 555-01{random.randint(10, 99)}",
                'estimated_price': f"${random.randint(80, 400)}"
            })
        return hotels

    @staticmethod
    def get_restaurants(city_name: str, lat: float, lon: float) -> List[Dict]:
        """Generate mock restaurants"""
        cuisines = ["Italian", "Indian", "Chinese", "Mexican", "Local", "Fusion", "Japanese"]
        types = ["Bistro", "Cafe", "Kitchen", "Grill", "House", "Diner"]
        
        restaurants = []
        for i in range(8):
            cuisine = random.choice(cuisines)
            name = f"{cuisine} {random.choice(types)}"
            r_lat, r_lon = MockData._add_random_offset(lat, lon)
            
            restaurants.append({
                'name': name,
                'address': f"{random.randint(1, 999)} Food Court, {city_name}",
                'rating': round(random.uniform(4.0, 5.0), 1),
                'price_level': random.randint(1, 3),
                'lat': r_lat,
                'lon': r_lon,
                'place_id': f"mock_rest_{i}",
                'types': [cuisine.lower(), "restaurant", "food"],
                'estimated_cost': f"${random.randint(20, 80)}"
            })
        return restaurants

    @staticmethod
    def get_attractions(city_name: str, lat: float, lon: float) -> List[Dict]:
        """Generate mock attractions"""
        types = [
            ("National Museum", "museum"),
            ("City Park", "park"),
            ("Central Mall", "shopping_mall"),
            ("Adventure Land", "amusement_park"),
            ("Historic Fort", "tourist_attraction"),
            ("Botanical Garden", "park"),
            ("Grand Market", "shopping_mall")
        ]
        
        attractions = []
        for i, (name_base, type_) in enumerate(types):
            a_lat, a_lon = MockData._add_random_offset(lat, lon)
            
            attractions.append({
                'name': f"{city_name} {name_base}",
                'address': f"Near City Center, {city_name}",
                'rating': round(random.uniform(4.2, 5.0), 1),
                'lat': a_lat,
                'lon': a_lon,
                'place_id': f"mock_attr_{i}",
                'types': [type_, "point_of_interest"],
                'photos': []
            })
        return attractions

    @staticmethod
    def get_itinerary(num_days: int, city_name: str, attractions: List[Dict], restaurants: List[Dict]) -> List[Dict]:
        """Generate a mock itinerary"""
        daily_plans = []
        
        for day in range(1, num_days + 1):
            # Select random items for the day
            day_attrs = random.sample(attractions, min(3, len(attractions)))
            day_rests = random.sample(restaurants, min(3, len(restaurants)))
            
            plan = {
                "activities": [
                    {
                        "time": "10:00 AM",
                        "activity": f"Visit {day_attrs[0]['name']}",
                        "duration": "2 hours"
                    },
                    {
                        "time": "2:00 PM",
                        "activity": f"Explore {day_attrs[1]['name']}",
                        "duration": "3 hours"
                    }
                ],
                "meals": [
                    {
                        "time": "9:00 AM", 
                        "type": "Breakfast", 
                        "restaurant": day_rests[0]['name']
                    },
                    {
                        "time": "1:00 PM", 
                        "type": "Lunch", 
                        "restaurant": day_rests[1]['name']
                    },
                    {
                        "time": "8:00 PM", 
                        "type": "Dinner", 
                        "restaurant": day_rests[2]['name']
                    }
                ]
            }
            if len(day_attrs) > 2:
                plan["activities"].append({
                    "time": "5:00 PM",
                    "activity": f"Evening walk at {day_attrs[2]['name']}",
                    "duration": "1.5 hours"
                })
                
            daily_plans.append(plan)
            
        return daily_plans
