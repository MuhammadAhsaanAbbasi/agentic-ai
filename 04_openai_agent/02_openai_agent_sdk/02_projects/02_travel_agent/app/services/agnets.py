from agents import (
    Agent, Runner, RunContextWrapper, InputGuardrail, GuardrailFunctionOutput, InputGuardrailTripwireTriggered, function_tool, AsyncOpenAI, OpenAIChatCompletionsModel
)
from typing import List, Dict, Union, Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field
import requests as rq
from dotenv import load_dotenv
from datetime import datetime
import json
import os

_ = load_dotenv()

RAPID_API_KEY=os.getenv("RAPID_API_KEY")
MODEL="o3-mini-2025-01-31"

# RAPID_API_KEY=os.getenv("RAPID_API_KEY")
# gemini_api_key=os.getenv("GEMINI_API_KEY")

#Reference: https://ai.google.dev/gemini-api/docs/openai
# external_client = AsyncOpenAI(
#     api_key=gemini_api_key,
#     base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
# )

# model = OpenAIChatCompletionsModel(
#     model="gemini-2.0-flash",
#     openai_client=external_client
# )

class TravelPlan(BaseModel):
    destination: str
    duration_days: int
    budget: float
    activities: List[str] = Field(default_factory=list, description="List of recommended activities")
    notes: Optional[str] = Field(description="Additional Notes or Recommendations")

class FlightRecommendation(BaseModel):
    airline: str
    departure_time: str
    arrival_time: str
    price: float
    direct_flight: bool
    recommendation_reason: str

class HotelRecommendation(BaseModel):
    name: str
    location: str
    price_per_night: float
    amenities: List[str]
    recommendation_reason: str

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
            self.session_start = datetime.now()

@function_tool
async def search_flights(wrapper: RunContextWrapper[UserContext], origin: str, arrival: str, date: str):
    """
    Asynchronously searches for flights based on the provided origin, arrival, and date.

    Parameters:
    - wrapper (RunContextWrapper[UserContext]): A wrapper containing user context information, including preferred airlines.
    - origin (str): The IATA code of the departure airport.
    - arrival (str): The IATA code of the destination airport.
    - date (str): The date of travel in the format 'YYYY-MM-DD'.

    Returns:
    - str: A JSON string containing a list of flight options, sorted by user preferences if provided.
    """
    url = "https://google-flights2.p.rapidapi.com/api/v1/searchFlights"

    querystring = {
        "departure_id": origin, "arrival_id": arrival,
        "outbound_date":date, "travel_class":"ECONOMY",
        "adults":"1","show_hidden":"1","currency":"USD",
        "language_code":"en-US","country_code":"US"
        }

    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": "google-flights2.p.rapidapi.com"
    }

    request = rq.get(url, headers=headers, params=querystring)

    flight_data = request.json()

    flight_options = flight_data["data"]["itineraries"]["topFlights"]

    if wrapper and wrapper.context:
        preferred_airlines = wrapper.context.preferred_airlines
        if preferred_airlines:
            # Sort itineraries so that those containing a preferred airline are at the top.
            flight_options.sort(
                key=lambda itinerary: not any(
                    flight['airline'] in preferred_airlines 
                    for flight in itinerary.get('flights', [])
                )
            )
            
            # Mark itineraries that include a flight from a preferred airline.
            for itinerary in flight_options:
                if any(
                    flight['airline'] in preferred_airlines 
                    for flight in itinerary.get('flights', [])
                ):
                    itinerary['preferred'] = True
        
    return json.dumps(flight_options)


# import requests as rq

@function_tool
async def search_hotel(wrapper: RunContextWrapper[UserContext], location: str, check_in: str, check_out: str, max_price: Optional[float] = None):
    url = "https://tripadvisor16.p.rapidapi.com/api/v1/hotels/searchLocation"
    querystring = {"query": location}
    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": "tripadvisor16.p.rapidapi.com"
    }
    request = rq.get(url, headers=headers, params=querystring)
    response = request.json()
    city_code = response["data"][0]["geoId"]

    url = "https://tripadvisor16.p.rapidapi.com/api/v1/hotels/searchHotels"
    querystring = {
        "geoId": city_code,
        "checkIn": check_in,
        "checkOut": check_out,
        "pageNumber": "1",
        "currencyCode": "USD"
    }
    request = rq.get(url, headers=headers, params=querystring)
    hotel_response = request.json()
    hotels = hotel_response["data"]["data"]

    # For each hotel, remove unwanted keys and fetch additional details
    for hotel in hotels:
        hotel_id = hotel["id"]
        hotel.pop("cardPhotos", None)
        hotel.pop("commerceInfo", None)

        details_url = "https://tripadvisor16.p.rapidapi.com/api/v1/hotels/getHotelDetails"
        details_query = {
            "id": hotel_id,
            "checkIn": check_in,
            "checkOut": check_out,
            "currency": "USD"
        }
        # details_headers = {
        #     "x-rapidapi-key": "fc39528b12msh1ae8e1931a36056p14d208jsna507409155f5",
        #     "x-rapidapi-host": "tripadvisor16.p.rapidapi.com"
        # }
        details_request = rq.get(details_url, headers=headers, params=details_query)
        details_response = details_request.json()

        hotel_amenities = details_response["data"]["amenitiesScreen"]
        hotel["amenities"] = hotel_amenities

        # Convert priceForDisplay (e.g., "$57") to a float value for filtering and sorting.
        price_str = hotel.get("priceForDisplay")
        if price_str:
            try:
                hotel["price"] = float(price_str.replace("$", "").replace(",", ""))
            except Exception:
                hotel["price"] = None
        else:
            hotel["price"] = None

    # Filter by max_price if provided
    if max_price is not None:
        hotels = [
            hotel for hotel in hotels 
            if hotel.get("price") is not None and hotel["price"] <= max_price
        ]

    # Apply user preferences if available
    if wrapper and wrapper.context:
        preferred_amenities = wrapper.context.hotel_amenities
        budget_level = wrapper.context.budget_level

        if preferred_amenities:
            for hotel in hotels:
                # Flatten the amenities list: include both the 'title' and each item in 'content'
                flat_amenities = []
                for amenity in hotel.get("amenities", []):
                    if "title" in amenity:
                        flat_amenities.append(amenity["title"])
                    if "content" in amenity:
                        flat_amenities.extend(amenity["content"])
                matching = [a for a in flat_amenities if a in preferred_amenities]
                hotel["matching_amenities"] = matching
                hotel["preference_score"] = len(matching)

            # Sort hotels by the preference score (higher first)
            hotels.sort(key=lambda x: x.get("preference_score", 0), reverse=True)

        # Apply budget level sorting if available
        if budget_level:
            if budget_level == "budget":
                hotels.sort(key=lambda x: x.get("price") if x.get("price") is not None else float('inf'))
            elif budget_level == "luxury":
                hotels.sort(key=lambda x: x.get("price") if x.get("price") is not None else 0, reverse=True)
            # For mid-range, we assume the max_price filter has already narrowed the results

    return json.dumps(hotels)
        

@function_tool
def get_weather_forecasts(latitude: float, longitude: float):
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



budget_analysis_agent = Agent(
    name="Budget Analysis Agent",
    instructions="""
    You Analyze travel budgets to determine if they are realistic for the destination & duration, consider factors like:
    - Average hotel costs in the destination
    - Average flight costs
    - Food & entertainment expenses
    - Local transportation

    Provide a clear analysis of whether the budget is realistic and why,
    If the Budget is not realistic, suggest a more appropriate budget.
    Don't be harsh at all, lean towards it being realistic unless it's
    really crazy. If no budget was mentioned, just assume it's realistic.
    """,
    output_type=BudgetAnalysis,
    model=MODEL
)

async def budget_guardrail(ctx, agent, input_data):
    """Check if the user's travel budget is realistic."""
    try:
        analysis_prompt = f"The user is planning a trip and said: {input_data}.\nAnalyze if their budget is realistic for a trip to their destination for the length they mentioned."
        result = await Runner.run(budget_analysis_agent, analysis_prompt, context=ctx.content)
        final_output = result.final_output_as(BudgetAnalysis)

        if not final_output.is_realistic:
            print(f"Your budget for your trip may not be realistic. {final_output.reasoning}" if not final_output.is_realistic else None)

        return GuardrailFunctionOutput(
            output_info=final_output,
            tripwire_triggered=not final_output.is_realistic
        )
    except Exception as e:
        return GuardrailFunctionOutput(
            output_info=BudgetAnalysis(is_realistic=True, reasoning=f"Error Analyzing Budget: {str(e)}"),
            tripwire_triggered=False
        )

flight_agent = Agent[UserContext](
    name="Flight Agent",
    handoff_description="Specialist agent for finding & recommending flights",
    instructions="""
    You're a flight specialist who helps users find the best flights for their trips.

    User the search_flights tool to find flight options & then provide personalized
    recommendations based on the user's preferences (price, time, direct vs connecting).

    The user's prefrences are available in the context, including preferred airlines.
    
    Always explain the reasoning behind your recommendations.

    Format your response in a clear, organized way with flight details and prices.
    """,
    tools=[search_flights],
    model=MODEL,
    output_type=FlightRecommendation,
)

hotel_agent = Agent[UserContext](
    name="Hotel Agent",
    handoff_description="Specialist agent for finding & recommending hotels",
    instructions="""
    You're a hotel specialist who helps users find the best hotels for their trips.

    User the search_hotel tool to find hotel options & then provide personalized
    recommendations based on the user's preferences (price, amenities).

    The user's prefrences are available in the context, including preferred amenities.

    Always explain the reasoning behind your recommendations.

    Format your response in a clear, organized way with hotel details and prices.
    """,
    tools=[search_hotel],
    model=MODEL,
    output_type=HotelRecommendation,
)

conversational_agent = Agent[UserContext](
    name="General Conversation Specialist",
    handoff_description="Specialist Agent for giving basics responses to the user to carry out a normal conversation as opposed to structured output.",
    instructions="""
    You're a trip planning expert who answers basic user questions about their trip & offers any suggestions. 
    Act as a helpful assistant and be helpful in any way you can be.
    """,
    model=MODEL,
)

travel_agent = Agent[UserContext](
    name="Travel Agent",
    instructions="""
    You're a travel specialist who helps users find the best flights & hotels for their trips.

    Use the flight_agent & hotel_agent to find flight & hotel options & then provide personalized
    recommendations based on the user's preferences (price, amenities, time, budget).

    The user's prefrences are available in the context, which you can use to tailer your recommendations.
    Always explain the reasoning behind your recommendations.

    You can:
    1. Get Weather forecasts for destinations.
    2. Hand off to specialized agents for flight & hotel recommendations.
    3. Create comprehensive travel plans with activities & notes

    Always be helpful, informative & enthusiastic about travelling.
    """,
    handoffs=[flight_agent, hotel_agent, conversational_agent],
    tools=[get_weather_forecasts],
    model=MODEL,
    input_guardrails=[
        InputGuardrail(
            guardrail_function=budget_guardrail
        )
    ],
    output_type=TravelPlan,
)

# async def main():
#     # Create a user context with some preferences
#     user_context = UserContext(
#         user_id="user123",
#         preferred_airlines=["SkyWays", "OceanAir"],
#         hotel_amenities=["WiFi", "Pool"],
#         budget_level="mid-range"
#     )
    
#     # Example queries to test different aspects of the system
#     queries = [
#         "I'm planning a trip to Miami for 5 days with a budget of $2000. What should I do there?",
#         "I'm planning a trip to Tokyo for a week, looking to spend under $5,000. Suggestions?",
#         "I need a flight from New York to Chicago tomorrow",
#         "Find me a hotel in Paris with a pool for under $400 per night",
#         "I want to go to Dubai for a week with only $300"  # This should trigger the budget guardrail
#     ]
    
#     for query in queries:
#         print("\n" + "="*50)
#         print(f"QUERY: {query}")
#         print("="*50)
        
#         try:
#             result = await Runner.run(travel_agent, query, context=user_context)
            
#             print("\nFINAL RESPONSE:")
            
#             # Format the output based on the type of response
#             if hasattr(result.final_output, "airline"):  # Flight recommendation
#                 flight = result.final_output
#                 print("\n✈️ FLIGHT RECOMMENDATION ✈️")
#                 print(f"Airline: {flight.airline}")
#                 print(f"Departure: {flight.departure_time}")
#                 print(f"Arrival: {flight.arrival_time}")
#                 print(f"Price: ${flight.price}")
#                 print(f"Direct Flight: {'Yes' if flight.direct_flight else 'No'}")
#                 print(f"\nWhy this flight: {flight.recommendation_reason}")
                
#                 # Show user preferences that influenced this recommendation
#                 airlines = user_context.preferred_airlines
#                 if airlines and flight.airline in airlines:
#                     print(f"\n👤 NOTE: This matches your preferred airline: {flight.airline}")
                
#             elif hasattr(result.final_output, "name") and hasattr(result.final_output, "amenities"):  # Hotel recommendation
#                 hotel = result.final_output
#                 print("\n🏨 HOTEL RECOMMENDATION 🏨")
#                 print(f"Name: {hotel.name}")
#                 print(f"Location: {hotel.location}")
#                 print(f"Price per night: ${hotel.price_per_night}")
                
#                 print("\nAmenities:")
#                 for i, amenity in enumerate(hotel.amenities, 1):
#                     print(f"  {i}. {amenity}")
                
#                 # Highlight matching amenities from user preferences
#                 preferred_amenities = user_context.hotel_amenities
#                 if preferred_amenities:
#                     matching = [a for a in hotel.amenities if a in preferred_amenities]
#                     if matching:
#                         print("\n👤 MATCHING PREFERRED AMENITIES:")
#                         for amenity in matching:
#                             print(f"  ✓ {amenity}")
                
#                 print(f"\nWhy this hotel: {hotel.recommendation_reason}")
                
#             elif hasattr(result.final_output, "destination"):  # Travel plan
#                 travel_plan = result.final_output
#                 print(f"\n🌍 TRAVEL PLAN FOR {travel_plan.destination.upper()} 🌍")
#                 print(f"Duration: {travel_plan.duration_days} days")
#                 print(f"Budget: ${travel_plan.budget}")
                
#                 # Show budget level context
#                 budget_level = user_context.budget_level
#                 if budget_level:
#                     print(f"Budget Category: {budget_level.title()}")
                
#                 print("\n🎯 RECOMMENDED ACTIVITIES:")
#                 for i, activity in enumerate(travel_plan.activities, 1):
#                     print(f"  {i}. {activity}")
                
#                 print(f"\n📝 NOTES: {travel_plan.notes}")
            
#             else:  # Generic response
#                 print(result.final_output)
                
#         except InputGuardrailTripwireTriggered as e:
#             print("\n⚠️ GUARDRAIL TRIGGERED ⚠️")

# import asyncio

# if __name__ == "__main__":
#     asyncio.run(main())