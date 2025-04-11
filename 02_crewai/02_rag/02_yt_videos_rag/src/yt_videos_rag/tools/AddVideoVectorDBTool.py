from crewai.tools import BaseTool
from typing import Type, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from embedchain import App
from embedchain.models.data_type import DataType
import requests
import os


class AddVideoVectorDBInput(BaseModel):
    """Input for FetchLatestVideosFromYTChannel."""
    video_url: str = Field(
        ...,
        description="The URL of the YouTube video to add to the vector database"
    )

class AddVideoVectorDBOutput(BaseModel):
    success: bool = Field(
        ...,
        description="Whether the video was successfulluy added to the vector DB."
    )

class AddVideoVectorDBTool(BaseTool):
    name: str = "Add video to Vector DB"
    description: str = (
        "Add a YouTube video to the Vector database"
    )
    args_schema: Type[BaseModel] = AddVideoVectorDBInput
    return_schema: Type[BaseModel] = AddVideoVectorDBOutput

    def _run(self, 
             video_url: str) -> AddVideoVectorDBOutput:
        try:
            app = App()
            app.add(video_url, data_type=DataType.YOUTUBE_VIDEO)
            return AddVideoVectorDBOutput(success=True)
        except Exception as e:
            print(e)
            return AddVideoVectorDBOutput(success=False)