from crewai_tools import ScrapeWebsiteTool, SerperDevTool
from dotenv import load_dotenv
import os

_ = load_dotenv()
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()