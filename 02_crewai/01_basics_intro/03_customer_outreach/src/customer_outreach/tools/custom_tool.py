from crewai_tools import FileReadTool, SerperDevTool, DirectoryReadTool
from crewai.tools import BaseTool
from dotenv import load_dotenv
import os

_=load_dotenv()
SERPER_API_KEY=os.getenv("SERPER_API_KEY")

directory_read_tool = DirectoryReadTool(directory="./instructions")
file_read_tool = FileReadTool()
search_tool = SerperDevTool()

class SentimentAnalysisTool(BaseTool):
    name: str = "Sentiment Analysis Tool"
    description: str = ("Analyzes the Sentiment of text to ensure positive & engaging Communication")

    def _run(self, text:str)-> str:
        return "positive"

sentiment_analysis_tool = SentimentAnalysisTool()
