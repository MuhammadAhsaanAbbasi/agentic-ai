from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from langchain_community.agent_toolkits import GmailToolkit
from langchain_community.tools.gmail import GmailCreateDraft
from langchain_community.tools.gmail import get_gmail_credentials
import os

current_file_path = os.path.abspath(__file__)
# print(f"current file: {current_file_path}")

# Get the parent directory of the current file's directory
parent_directory = os.path.dirname(current_file_path)
# print(f"parent file: {parent_directory}")

# Get the parent directory of the parent directory
Child_DIR = os.path.dirname(parent_directory)


# Get the Chlid directory of the parent directory
BASE_DIR = os.path.dirname(Child_DIR)

# print(f"BASE_DIR: {BASE_DIR}")

# Define the path to the client_secret.json file
CLIENT_SECRET_FILE = os.path.join(BASE_DIR, 'credentials.json')

# print(f'secret file: {CLIENT_SECRET_FILE}')
resource = get_gmail_credentials(client_secrets_file=CLIENT_SECRET_FILE)


class DraftInput(BaseModel):
    """Input schema for MyCustomTool."""
    data: str = Field(..., description="""
        The input to this tool should be a pipe (|) sperated text
        of length 3 (three), representating who to send email to,
        the subject of the email and the actual message.
        For Example, `lorem@ipsum.com|Again Meeting|Hey, It was great meetup, let's scheduled a new meeting on this week.`
    """
)

class GmailDraftor(BaseTool):
    name: str = "GmailDraftor"
    description: str = ("""
        Use this tool to create an email draft in the user's Gmail account.
        It is helpful when you want to compose a message that can later be reviewed and sent by the user. 
        The input should be a single string with three parts, separated by a pipe character '|'. 
        These parts are: recipient email address, subject line, and the body of the email. 
        Example input: 'john.doe@example.com|Meeting Follow-up|Hi John, just following up on our discussion from earlier today.'
        This tool is ideal for summarizing information or automating message drafting for follow-ups, reports, or outreach.
    """
    )

    args_schema: Type[BaseModel] = DraftInput

    def _run(self, data):
        # Implementation goes here
        email, subject, message = data.split("|")
        gmail = GmailToolkit(api_resource=resource).model_rebuild()
        draft  = GmailCreateDraft(api_resource=gmail.api_resource)

        result = draft({
            "to": [email],
            "subject": subject,
            "message": message
        })

        return f"Draft Created: {result}\n"