import asyncio
from typing import List
from pydantic import BaseModel, Field
from agents import Agent, Runner
from dotenv import load_dotenv

_ = load_dotenv()

class TravelPlan(BaseModel):
    destination: str = Field(description="The destination of the travel plan")
    duration_days: int = Field(description="The duration of the travel plan in days")
    budget: float = Field(description="The budget for the travel plan in USD")
    activities: List[str] = Field(description="A list of activities for the travel plan")
    notes: str = Field(description="Any additional notes or recommendations for the travel plan")

travel_agent = Agent(
    name="Travel Planner",
    instructions="""
    You're comprehensive travel planning assistant that help users plan their perfect trip.
    You can create personalized travel itineraries based on the user's interests & preferences.
    Always be helpful, informative & enthusiastic about travel. Provide specific 
    recommendations based on the user's interests & preferences.

    When creating a travel plan, considers:
    - Local attractions & activities
    - Budget constraints
    - Travel duration
    - User's interests & preferences
    """,
    output_type=TravelPlan,
    model="o1-pro-2025-03-19"
)

async def main():
    queries = [
        "I'm planning a trip to Paris. I have a budget of $2000 and want to stay for 7 days. I like art museums and historical sites.",
        "I'm planning a trip to Tokyo. I have a budget of $3000 and want to stay for 10 days. I like shopping and food.",
        "I'm planning a trip to New York. I have a budget of $4000 and want to stay for 5 days. I like the Empire State Building and the Statue of Liberty.",
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