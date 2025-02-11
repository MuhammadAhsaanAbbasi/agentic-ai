from crewai_tools import ScrapeWebsiteTool, SerperDevTool
from crewai.tools import BaseTool
from dotenv import load_dotenv
import os

_=load_dotenv()
SERPER_API_KEY=os.getenv("SERPER_API_KEY")

# Initialize the tools
search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()