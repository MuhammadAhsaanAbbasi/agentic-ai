from agents import Agent, Runner, function_tool
from pydantic import BaseModel, Field
from typing import List, Dict, Union, Optional
from dotenv import load_dotenv
import asyncio
import requests as rq
import datetime
import json

load_dotenv()

class FlightRecommendation(BaseModel):
    aireline: str
    departure_time: str
    arrival_time: str
    price: float
    driect_flight: bool
    recommendation_reason: str

class HotelRecommendation(BaseModel):
    name: str
    location: str
    price_per_night: float
    amenities: List[str]
    recommendation_reason: str

class TravelPlan(BaseModel):
    destination: str = Field(description="The destination of the travel plan")
    duration_days: int = Field(description="The duration of the travel plan in days")
    budget: float = Field(description="The budget for the travel plan in USD")
    activities: List[str] = Field(description="A list of activities for the travel plan")
    notes: str = Field(description="Any additional notes or recommendations for the travel plan")

@function_tool
def get_weather(latitude: float, longitude: float):
    """Get weather data for a given latitude and longitude."""
    BASE_URL = f"https://api.open-meteo.com/v1/forecast"
    params: Dict[str, Union[str, int, float]] = {
        "latitude" : latitude,
        "longitude" : longitude,
        "hourly" : "temperature_2m",
        "forecast_days" : 1
    }

    response = rq.get(BASE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
    else:
        raise Exception(f"API Request Failed: {response.status_code}, {response.text}")

    current_time = datetime.datetime.utcnow()
    time_list = [datetime.datetime.fromisoformat(t.replace("Z", "+00:00")) for t in data["hourly"]["time"]]
    temperature_lists = data["hourly"]["temperature_2m"]

    closet_time_index = min(range(len(time_list)), key=lambda i: abs(time_list[i] - current_time))

    temperature = temperature_lists[closet_time_index]

    return f"The Current temperature at {latitude}, {longitude} is {temperature}°C"

@function_tool
def search_flights(origin: str, destination: str, date: str) -> str:
    """Search for flights between two cities on a specific date."""
    # In a real implementation, this would call a flight search API
    flight_options = [
        {
            "airline": "SkyWays",
            "departure_time": "08:00",
            "arrival_time": "10:30",
            "price": 350.00,
            "direct": True
        },
        {
            "airline": "OceanAir",
            "departure_time": "12:45",
            "arrival_time": "15:15",
            "price": 275.50,
            "direct": True
        },
        {
            "airline": "MountainJet",
            "departure_time": "16:30",
            "arrival_time": "21:45",
            "price": 225.75,
            "direct": False
        }
    ]
    
    return json.dumps(flight_options)

@function_tool
def search_hotels(city: str, check_in: str, check_out: str, max_price: Optional[float] = None) -> str:
    """Search for hotels in a city for specific dates within a price range."""
    # In a real implementation, this would call a hotel search API
    hotel_options = [
        {
            "name": "City Center Hotel",
            "location": "Downtown",
            "price_per_night": 199.99,
            "amenities": ["WiFi", "Pool", "Gym", "Restaurant"]
        },
        {
            "name": "Riverside Inn",
            "location": "Riverside District",
            "price_per_night": 149.50,
            "amenities": ["WiFi", "Free Breakfast", "Parking"]
        },
        {
            "name": "Luxury Palace",
            "location": "Historic District",
            "price_per_night": 349.99,
            "amenities": ["WiFi", "Pool", "Spa", "Fine Dining", "Concierge"]
        }
    ]
    
    # Filter by max price if provided
    if max_price is not None:
        filtered_hotels = [hotel for hotel in hotel_options if hotel["price_per_night"] <= max_price]
    else:
        filtered_hotels = hotel_options
        
    return json.dumps(filtered_hotels)


flight_agent = Agent(
    name="Flight Specialist",
    handoff_description="Specialize agent for finding & recommending flights",
    instructions="""
    You're a flight specialist agent that helps users find the best flights for their trips.

    Use the search_filghts tool to find flight options & then provide personalized recommedation
    based on the user's preferences (price, time, direct vs connecting).

    Always explain the resoaning behind your recommendations.

    Format your responses in a clear, organized way with flight details & prices.
    """,
    output_type=FlightRecommendation,
    tools=[search_flights],
    model="o1-pro-2025-03-19"
)

hotel_agent = Agent(
    name="Hotel Specialist",
    handoff_description="Specialize agent for finding & recommending hotels & accommodations",
    instructions="""
    You're a hotel specialist agent that helps users find the best hotels/accomodations for their trips.

    Use the search_hotels tool to find hotel options & then provide personalized recommedation
    based on the user's preferences (price, amenities, location).

    Always explain the resoaning behind your recommendations.

    Format your responses in a clear, organized way with hotel details & prices.
    """,
    output_type=HotelRecommendation,
    tools=[search_hotels],
    model="o1-pro-2025-03-19"
)

travel_agent = Agent(
    name="Travel Planner",
    instructions="""
    You're a comprehensive travel planning assistnts that help users plan their perfect trip.
    You can:
    1.) provide weather information for destinations
    2.) Create personalized travel itineraries
    3.) Hand off to specialists for flights & hotels when needed.

    Always be helpful, informative & enthusiastic about travel. provide specific recommendations based on the user's interests & preferences.

    When creating travel plans, consider:
    - The weather at the destination
    - Local attractions & activities
    - Budget constraints
    - Travel Duration

    If the user asks specifically about flights or hotels, hand off to the appropriate specialist agent.
    """,
    output_type=TravelPlan,
    tools=[get_weather],
    handoffs=[flight_agent, hotel_agent],
    model="o1-pro-2025-03-19"
)


async def main():
    queries = [
        "I need a flight from New York to Chicago today",
        "Find me a hotel in Paris with a pool for under $300 per night",
        "Plan a 7-day trip to Tokyo, considering the weather and budget of $3000"
    ]

    for query in queries:
        print(f"Query: {query}")
        response = await Runner.run(travel_agent, query)

        if hasattr(response.final_output, "airline"):
            flight = response.final_output
            print("\n✈️ FLIGHT RECOMMENDATION ✈️") # Format the output in nicer way
            print(f"Airline: {flight.airline}")
            print(f"Departure Time: {flight.departure_time}")
            print(f"Arrival Time: {flight.arrival_time}")
            print(f"Price: ${flight.price}")
            print(f"Direct Flight: {flight.direct_flight}")
            print(f"Recommendation Reason: {flight.recommendation_reason}")
        
        elif hasattr(response.final_output, "name") and hasattr(response.final_output, "amenities"):
            hotel = response.final_output
            print("\n🏨 HOTEL RECOMMENDATION 🏨") # Format the output in nicer way
            print(f"Name: {hotel.name}")
            print(f"Location: {hotel.location}")
            print(f"Price per Night: ${hotel.price_per_night}")

            print(f'\n Amenities')
            for i, amenity in enumerate(hotel.amenities, start=1):
                print(f"{i}. {amenity}")
            
            print(f"Recommendation Reason: {hotel.recommendation_reason}")
        
        elif hasattr(response.final_output, "destination"):
            travel_plan = response.final_output
            print("\n🌍 TRAVEL PLAN 🌍") # Format the output in nicer way
            print(f"Destination: {travel_plan.destination}")
            print(f"Duration: {travel_plan.duration_days} days")
            print(f"Budget: ${travel_plan.budget}")
            
            print(f"\n🎯 RECOMMENDED ACTIVITIES:")
            for i, activity in enumerate(travel_plan.activities, start=1):
                print(f"{i}. {activity}")

            print(f"\n📝 Notes: {travel_plan.notes}")
        
        else:
            print(f"No specific recommendation found. {response.final_output}")


if __name__ == "__main__":
    asyncio.run(main())