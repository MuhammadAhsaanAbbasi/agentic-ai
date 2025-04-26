from google.adk.agents import Agent
from google.adk.tools import google_search
from dotenv import load_dotenv
import app.tools as agent_tool

from adktools import discover_adk_tools

_ = load_dotenv()


root_agent = Agent(
    name="root_agent",
    description=(
        "Agent to answer questions about time OR weather in a city."
    ),
    instruction=(
        "You are a helpful agent whom primary goal is to provide the weather & the current time for give timezones or cities."
        "When the user asks about the weather in a specific city  or time zone so using `google_search` tool to find his latitude & longitude" 
        "then on given values using `get_weather` tool to get the weather of that city or timezone."
        "When the user asks about the time in a specific city or time zone so using `get_time` tool to get the time of that city or timezone."
        "Analyze the tool's response: if the status is error, inform the user politely about the error message."
        "If the status is `success`, present the user with the information clearly and concisely to the user."
        "Only use the tools when appropriate for a weather & time related request."
    ),
    tools=discover_adk_tools(agent_tool),
    model="gemini-2.5-flash-preview-04-17"
)