from agents import (
    Agent, Runner, function_tool, RunContextWrapper, InputGuardrail, GuardrailFunctionOutput, InputGuardrailTripwireTriggered
    )
from pydantic import BaseModel, Field
from typing import List, Dict, Union, Optional
from dataclasses import dataclass
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

class BudgetAnalysis(BaseModel):
    is_realistic: bool
    reasoning: str
    suggested_budget: Optional[float] = None


@dataclass
class UserContext:
    user_id: str
    preferred_airlines: List[str] = None
    hotel_amenities: List[str] = None
    budget_level: str = None
    session_start: datetime = None
    
    def __post_init__(self):
        if self.preferred_airlines is None:
            self.preferred_airlines = []
        if self.hotel_amenities is None:
            self.hotel_amenities = []
        if self.session_start is None:
            self.session_start = datetime.datetime.now()

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
def search_flights(wrapper: RunContextWrapper[UserContext] , origin: str, destination: str, date: str) -> str:
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
    
    if wrapper and wrapper.context:
        preferred_airlines = wrapper.context.preferred_airlines
        if preferred_airlines:
            flight_options.sort(key=lambda x: x["airline"] not in preferred_airlines)

            for flight in flight_options:
                if flight["airline"] in preferred_airlines:
                    flight["preferred"] = True
    
    return json.dumps(flight_options)

@function_tool
def search_hotels(wrapper: RunContextWrapper[UserContext] ,city: str, check_in: str, check_out: str, max_price: Optional[float] = None) -> str:
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
        
    if wrapper and wrapper.context:
        preferred_amenities = wrapper.context.hotel_amenities
        budget_level = wrapper.context.budget_level

        if preferred_amenities:

            for hotel in filtered_hotels:
                matching_amenities = [a for a in hotel["ameities"] if a in preferred_amenities]
                hotel["matching_amenities"] = matching_amenities
                hotel["preference_score"] = len(matching_amenities)

            filtered_hotels.sort(key=lambda x: x["preference_score"], reverse=True)
        
        if budget_level:
            if budget_level == "budget":
                filtered_hotels = [hotel for hotel in filtered_hotels if hotel["price_per_night"] < 200]
            elif budget_level == "luxury":
                filtered_hotels = [hotel for hotel in filtered_hotels if hotel["price_per_night"] >= 300]
    
    return json.dumps(filtered_hotels)

budget_analysis_agent = Agent(
    name="Budget Analyzer",
    instructions="""
    You analyze travel budgets to determine if they are realistic for the destination and duration.
    Consider factors like:
    - Average hotel costs in the destination
    - Flight costs
    - Food and entertainment expenses
    - Local Transportation

    Provide a clear analysis of Whether the budget is realistic and why.
    If the budget is not realistic, suggest a more appropriate budget.
    Don't be harsh at all, lean towards it being realistic unless it's really crazy.
    If no budget was mentioned, just assume it is realistic.
    """,
    output_type=BudgetAnalysis,
    model="o1-pro-2025-03-19"
)

async def budget_guardrail(ctx, agent, input_data):
    """Check if the user's travel budget is realistic"""
    try:
        analysis_prompt = f"The user is planning a trip & said: {input_data}.\nAnalyze if their budge is realistic for a trip to their destination for the lenght they mentioned."
        result = await Runner.run(budget_analysis_agent, analysis_prompt, context=ctx.context)
        final_output = result.final_output_as(BudgetAnalysis)

        if not final_output.is_realistic:
            print(f"Your Budgets for your trip may not be realistic. {final_output.reasoning}" if not final_output.is_realistic else None)
        
        return GuardrailFunctionOutput(
            output_info=final_output,
            tripwire_triggered=not final_output.is_realistic
        )
    except Exception as e:
        # Handle any errors gracefully
        return GuardrailFunctionOutput(
            output_info=BudgetAnalysis(is_realistic=True, reasoning=f"Error analyzing budget: {str(e)}"),
            tripwire_triggered=False
        )

flight_agent = Agent[UserContext](
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

hotel_agent = Agent[UserContext](
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

conversational_agent = Agent[UserContext](
    name="General Conversation Specialist",
    handoff_description="Specialist Agent for given baisc responses to the user to carry out a normal conversation as opposed to structured output.",
    instructions="""
    You're a trip planning expert who answers basic user questions about their trip & offers any suggestions.
    Act as a helpful assistant and be helpful in anyway you can be.
    """,
    model="o1-pro-2025-03-19"
)

travel_agent = Agent[UserContext](
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
    handoffs=[flight_agent, hotel_agent, conversational_agent],
    input_guardrails=[
        InputGuardrail(
            guardrail_function=budget_guardrail
        )
    ],
    model="o1-pro-2025-03-19"
)


async def main():
    user_context = UserContext(
        user_id="user123",
        preferred_airlines=["SkyWays", "OceanAir"],
        hotel_amenities=["WiFi", "Pool"],
        budget_level="mid-range"
    )
    
    # Example queries to test different aspects of the system
    queries = [
        "I'm planning a trip to Miami for 5 days with a budget of $2000. What should I do there?",
        "I'm planning a trip to Tokyo for a week, looking to spend under $5,000. Suggestions?",
        "I need a flight from New York to Chicago tomorrow",
        "Find me a hotel in Paris with a pool for under $400 per night",
        "I want to go to Dubai for a week with only $300"  # This should trigger the budget guardrail
    ]
    

    for query in queries:
        print(f"Query: {query}")
        try:
            response = await Runner.run(travel_agent, query, context=user_context)

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
        except InputGuardrailTripwireTriggered as e:
            print(f"Guardrail triggered: {e}")


if __name__ == "__main__":
    asyncio.run(main())