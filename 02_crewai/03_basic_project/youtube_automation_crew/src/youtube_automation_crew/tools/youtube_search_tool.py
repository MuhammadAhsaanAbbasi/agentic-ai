from crewai.tools import BaseTool
from typing import Type, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import os
import requests

class VideoSearchResult(BaseModel):
    """Model for a single video search result."""
    video_id: str
    title: str
    channel_id: str
    channel_title: str
    days_since_published: int

class YoutubeVideoSearchToolInput(BaseModel):
    """Input for the YoutubeVideoSearchTool."""
    keyword: str = Field(...,description="The keyword to search for on YouTube.")
    max_results: int = Field(..., description="The maximum number of results to return.")

class YoutubeVideoSearchTool(BaseTool):
    """Tool for searching YouTube videos."""
    name: str = "Youtube Search Tool"
    description: str = "Searches YouTube for videos based on a keyword & returns a list of video search results."
    args_schema: Type[BaseModel] = YoutubeVideoSearchToolInput

    def _run(self, keyword: str, max_results: int) -> List[VideoSearchResult]:
        api_key = os.environ.get("YOUTUBE_API_KEY")
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": keyword,
            "type": "video",
            "maxResults": max_results,
            "key": api_key
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        items = response.json().get("items", [])

        results = []
        for item in items:
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            channel_id = item["snippet"]["channelId"]
            channel_title = item["snippet"]["channelTitle"]
            publish_date = datetime.fromisoformat(
                item["snippet"]["publishedAt"].replace("Z", "+00:00")).astimezone(timezone.utc)
            days_since_published = (datetime.now(timezone.utc) - publish_date).days
            results.append(VideoSearchResult(
                video_id=video_id,
                title=title,
                channel_id=channel_id,
                channel_title=channel_title,
                days_since_published=days_since_published
            ))
        
        return results
