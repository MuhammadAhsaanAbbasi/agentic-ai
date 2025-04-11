from pydantic import BaseModel, Field
from typing import Optional, List

class ContentCreatorInfo(BaseModel):
    first_name: Optional[str] = Field(..., description="The first name of the content creator")
    last_name: Optional[str] = Field(
        None, description="The last name of the content creator"
    )
    main_topics_covered: Optional[List[str]] = Field(
        None, description="The main topics covered by the conent creator"
    )
    bio: Optional[str] = Field(
        None, description="A brief biography of the content creator"
    )
    email_address: Optional[str] = Field(
        None, description="The email address of the content creator"
    )
    linkedin_url: Optional[str] = Field(
        None, description="The LinkedIn profile URL of the content creator"
    )
    has_linkedin: Optional[bool] = Field(
        None, description="Whether the content creator has a LinkedIn profile"
    )
    x_url: Optional[str] = Field(
        None, description="The X (Twitter) profile URL of the content creator"
    )
    has_twitter: Optional[bool] = Field(
        None, description="Whether the content creator has a X (Twitter) profile"
    )
    instagram_url: Optional[str] = Field(
        None, description="The Instagram profile URL of the content creator"
    )
    has_instagram: Optional[bool] = Field(
        None, description="Whether the content creator has an Instagram profile"
    )