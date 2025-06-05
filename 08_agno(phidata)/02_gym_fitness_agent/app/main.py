import os
from agno.agent import Agent
from agno.tools.webbrowser import WebBrowserTools
from agno.models.groq import Groq
from dotenv import load_dotenv

load_dotenv()

llm = Groq(api_key=os.getenv("GROQ_API_KEY"), name="llama-3.3-70b-versatile")

class BaseAgent:
    def __init__(self, name: str, tools: list, instructions: str):
        self.name = name
        self.tools = tools
        self.instructions = instructions

    def run(self, input: str):
        agent = Agent(
            name=self.name,
            tools=self.tools,
            instructions=self.instructions,
            model=llm,
            # verbose=True
        )
        response = agent.run(input)
        return response.content

class WebAgent(BaseAgent):
    def __init__(self, name: str):
        super().__init__(name, [WebBrowserTools()], 
                         "You are a web agent that can browse the web and answer questions about the web.")


agent = WebAgent("WebAgent")
response = agent.run("Open Youtube music and play phool song by aur")
print(response)