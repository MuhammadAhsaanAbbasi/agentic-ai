from agents import Agent, Runner, function_tool
from pydantic import BaseModel, Field
from typing import List, Dict, Union
from dotenv import load_dotenv
import asyncio
import requests as rq
import datetime

load_dotenv()


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


travel_agent = Agent(
    name="Travel Planner",
    instructions="""
    You're a comprehensive travel planning assistant that helps users plan their perfect trip.
    You can create personalized travel itineraries based on the user's interests & preferences.

    You can:
    1.) Provide Weather information for destinations
    2.) Create personalized travel itineraries

    Always be helpful, information & enthusiastic about travel. Provide specific 
    recommendations based on the user's interests & preferences.

    When creating travel plans, consider:
    - The Weather at the destination
    - Local attractions & activities
    - Budget constraints
    - Travel duration
    - User's interests & preferences
    """,
    output_type=TravelPlan,
    tools=[get_weather],
    model="o1-pro-2025-03-19"
)


async def main():
    queries = [
        "I'm planning a trip to Paris. I have a budget of $2000 and want to stay for 7 days. I like art museums and historical sites. What should I do there and what is the weather going to look like?",
        "I'm planning a trip to Tokyo. I have a budget of $3000 and want to stay for 10 days. I like shopping and food. What activities do you recommend based on the weather?",
        "I'm planning a trip to New York. I have a budget of $4000 and want to stay for 5 days. I like the Empire State Building and the Statue of Liberty. What should I do there and what is the weather going to look like?",
    ]

    for query in queries:
        print(f"Query: {query}")
        response = await Runner.run(travel_agent, query)
        
        travel_plan = response.final_output

        # Format the output in nicer way
        print(f"\n🌍 Travel Plan FOR: {travel_plan.destination.upper()} 🌍")
        print(f"\n⏱️ Duration: {travel_plan.duration_days} Days")
        print(f"\n💸 Budget: {travel_plan.duration_days} Days")
        print("\n🎯 RECOMMENDED ACTIVITIES:")
        for i, activity in enumerate(travel_plan.activities, start=1):
            print(f"{i}. {activity}")

        print(f"\n📝 Notes: {travel_plan.notes}")

if __name__ == "__main__":
    asyncio.run(main())