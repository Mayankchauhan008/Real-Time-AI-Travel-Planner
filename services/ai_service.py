import openai
import json
from typing import Dict, List

class AIService:
    def __init__(self, api_key: str):
        openai.api_key = api_key
    
    def generate_daily_plan(self, day_num: int, destination: str, 
                           interests: List[str], hotels: List[Dict],
                           restaurants: List[Dict], attractions: List[Dict]) -> Dict:
        """Generate AI-powered daily itinerary with real places"""
        
        # Create context with real places
        hotel_names = [h['name'] for h in hotels[:3]]
        restaurant_list = [f"{r['name']} ({r['estimated_cost']})" for r in restaurants[:5]]
        attraction_list = [f"{a['name']} (Rating: {a['rating']})" for a in attractions[:5]]
        
        prompt = f"""Create a detailed itinerary for Day {day_num} in {destination}.

Available REAL Hotels (user will stay at one):
{', '.join(hotel_names)}

Available REAL Restaurants:
{', '.join(restaurant_list)}

Available REAL Attractions:
{', '.join(attraction_list)}

User interests: {', '.join(interests)}

Create a realistic day plan with:
1. 3-4 activities from the attractions list above (use exact names)
2. Breakfast, lunch, dinner from restaurants list (use exact names)
3. Realistic timing (9 AM - 9 PM)
4. Travel time between activities

Return ONLY valid JSON in this format:
{{
    "activities": [
        {{"time": "9:00 AM", "activity": "exact attraction name from list", "duration": "2 hours"}},
    ],
    "meals": [
        {{"time": "8:00 AM", "type": "Breakfast", "restaurant": "exact restaurant name from list"}},
    ]
}}"""

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a travel planner. Return only valid JSON. Use EXACT names from the provided lists."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            # Extract JSON
            start = content.find('{')
            end = content.rfind('}') + 1
            json_str = content[start:end]
            
            return json.loads(json_str)
            return json.loads(json_str)
        except Exception as e:
            print(f"AI generation error: {e}")
            from utils.mock_data import MockData
            # Create a simple fallback itinerary based on available places
            return MockData.get_itinerary(1, destination, attractions, restaurants)[0]