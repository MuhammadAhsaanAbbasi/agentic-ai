from agents import (
    Agent, Runner, RunContextWrapper, InputGuardrail, GuardrailFunctionOutput, InputGuardrailTripwireTriggered, function_tool
)
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field
import requests as rq
from dotenv import load_dotenv
from datetime import datetime
import json

_ = load_dotenv()

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
    address: str
    price_per_night: float
    amenities: List[str]
    recommendation_reason: str

@dataclass
class UserContext:
    user_id: str
    preferred_airlines: List[str] = None
    hotel_amenities: List[str] = None
    budget_level: str = None
    session_start: datetime = None

@function_tool
async def search_flight(wrapper: RunContextWrapper[UserContext]):
    url = "https://google-flights2.p.rapidapi.com/api/v1/searchFlights"

    querystring = {
        "departure_id":"LON", "arrival_id":"MIA",
        "outbound_date":"2025-04-05", "travel_class":"ECONOMY",
        "adults":"1","show_hidden":"1","currency":"USD",
        "language_code":"en-US","country_code":"US"
        }

    headers = {
        "x-rapidapi-key": "fc39528b12msh1ae8e1931a36056p14d208jsna507409155f5",
        "x-rapidapi-host": "google-flights2.p.rapidapi.com"
    }

    request = rq.get(url, headers=headers, params=querystring)

    response = request.json()
