from crewai.tools import BaseTool
from typing import Type, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import os
import requests

class VideoDetails(BaseModel):
    """Model for a single video search result."""
    title: str
    description: str
    view_count: int
    like_count: int
    dislike_count: int
    comment_count: int
    channel_subscriber_count: int

class YoutubeVideoDetailsToolInput(BaseModel):
    """Input for the YoutubeVideoSearchTool."""
    video_id: str = Field(...,description="The ID of the YouTube Video.")

class YouTubeVideoDetailsTool(BaseTool):
    name: str = "YouTube Video Details"
    description: str = "Fetches details for a YouTube video."
    args_schema: Type[BaseModel] = YoutubeVideoDetailsToolInput

    def _run(self, video_id: str) -> List[VideoDetails]:
        """Fetches details for a YouTube video."""
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            raise ValueError("YOUTUBE_API_KEY environment variable is not set.")

        url = f"https://www.googleapis.com/youtube/v3/videos"
        params = {
            'part': 'snippet,statistics',
            'id': video_id,
            'key': api_key
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if 'items' not in data or len(data['items']) == 0:
            raise ValueError(f"No video found with ID: {video_id}")

        item = data['items'][0]
        snippet = item['snippet']
        statistics = item['statistics']

        channel_id = snippet['channelId']
        channel_url = "https://www.googleapis.com/youtube/v3/channels"
        channel_params = {
            'part': 'statistics',
            'id': channel_id,
            'key': api_key
        }

        channel_response = requests.get(channel_url, params=channel_params)
        channel_response.raise_for_status()
        channel_items = channel_response.json().get('items', [])[0]
        channel_subscriber_count = channel_items['statistics'].get('subscriberCount', 0)

        return [
            VideoDetails(
                title=snippet['title'],
                description=snippet['description'],
                view_count=int(statistics['viewCount']),
                like_count=int(statistics['likeCount']),
                dislike_count=int(statistics.get("dislikeCount", 0)),
                comment_count=int(statistics.get("commentCount", 0)),
                channel_subscriber_count=channel_subscriber_count  # This would require a separate API call to fetch the channel's subscriber count
            )
        ]
