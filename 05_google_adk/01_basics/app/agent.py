from google.adk.agents import Agent
from google.adk.tools import google_search
from dotenv import load_dotenv
_ = load_dotenv()


root_agent = Agent(
    name="root_agent",
    description=(
        "Agent to answer questions about time OR weather in a city."
    ),
    instruction=(
        "You are a helpful agent who can answer user questions about time OR weather in a city."
    ),
    tools=[google_search],
    model="gemini-2.5-flash-preview-04-17"
)