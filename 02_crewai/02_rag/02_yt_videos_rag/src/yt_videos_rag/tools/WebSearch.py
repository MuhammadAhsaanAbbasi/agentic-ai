from langchain_community.tools.tavily_search import TavilySearchResults
from crewai.tools import BaseTool
from typing import Type, List
from pydantic import BaseModel, Field
# from datetime import datetime, timezone
# from embedchain import App
# from embedchain.models.data_type import DataType
from dotenv import load_dotenv

_ = load_dotenv()

class WebSearchInput(BaseModel):
    """Input for WebSearchTool."""
    question: str = Field(
        ...,
        description="The question & query of the user they want to search it out."
    )


class WebSearchTool(BaseTool):
    name: str = "Web Search Tool"
    description: str = (
        """This tool is useful when we want web search for current events."""
    )
    args_schema: Type[BaseModel] = WebSearchInput

    def _run(self, 
             question: str):
        try:
                # Function logic here
            # Step 1: Instantiate the Tavily client with your API key
            websearch = TavilySearchResults()
            # Step 2: Perform a search query
            response = websearch.invoke({"query":question})
            return response
        except Exception as e:
            print(e)
