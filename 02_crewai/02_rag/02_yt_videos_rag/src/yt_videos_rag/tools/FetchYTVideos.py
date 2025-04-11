from crewai.tools import BaseTool
from typing import Type, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import requests
import os


class FetchLatestVideosFromYTChannelInput(BaseModel):
    """Input for FetchLatestVideosFromYTChannel."""
    youtube_channel_handle: str = Field(..., 
        description="The YouTube channel handle to fetch videos (e.g., '@channelhandle')"
    )
    max_results: int = Field(
        default=10,
        description="The maximum number of videos to return in results"
    )

class VideoInfo(BaseModel):
    video_id: str
    title: str
    publish_date: datetime
    video_url: str

class FetchLatestVideosFromYTChannelOutput(BaseModel):
    videos: List[VideoInfo]

class FetchLatestVideosFromYTChannel(BaseTool):
    name: str = "FetchLatestVideosFromYTChannel"
    description: str = (
        "Fetches the latest videos for a specified YouTube channel handle"
    )
    args_schema: Type[BaseModel] = FetchLatestVideosFromYTChannelInput
    return_schema: Type[BaseModel] = FetchLatestVideosFromYTChannelOutput

    def _run(self, 
             youtube_channel_handle: str, 
             max_results: int = 10) -> FetchLatestVideosFromYTChannelOutput:
        api_key = os.getenv("YOUTUBE_API_KEY")

        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "type": "channel",
            "q": youtube_channel_handle,
            "key": api_key
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        items = response.json().get("items", [])
        if not items:
            raise ValueError(f"No channel found for handle: {youtube_channel_handle}")
        
        channel_id = items[0]["id"]["channelId"]

        channel_params = {
            "part": "snippet",
            "channelId": channel_id,
            "maxResults": max_results,
            "order": "date",
            "type" : "video",
            "key": api_key
        }

        response = requests.get(url, params=channel_params)
        response.raise_for_status()
        items = response.json().get("items", [])

        videos = []
        for item in items:
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            publish_date = datetime.fromisoformat(
                item["snippet"]["publishedAt"].replace("Z", "+00:00")
            ).astimezone(timezone.utc)
            
            videos.append(
                VideoInfo(
                    video_id=video_id,
                    title=title,
                    publish_date=publish_date,
                    video_url=f"https://www.youtube.com/watch?v={video_id}"
                )
            )
        
        return FetchLatestVideosFromYTChannelOutput(videos=videos)