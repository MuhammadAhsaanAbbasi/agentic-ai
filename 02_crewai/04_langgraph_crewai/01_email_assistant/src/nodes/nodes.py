from langchain_community.agent_toolkits import GmailToolkit
from langchain_community.tools.gmail.search import GmailSearch
import time
from langchain_community.tools.gmail import get_gmail_credentials
import os
# Load the secrets file
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


class Nodes():
    def __init__(self):
        self.gmail = GmailToolkit(api_resource=resource)
    
    def check_new_emails(self, state):
        search = GmailSearch(api_resource=self.gmail.api_resource)
        emails = search('after:newer_than:1d')
        checked_emails = state["checked_emails_ids"] if state["checked_emails_ids"] else []

        thread = []
        new_emails = []
        print(f"Here are the emails: {emails}")
        for email in emails:
            if (email["id"] not in checked_emails) and (email["id"] not in thread) and (os.environ.get("MY_EMAIL") not in email["sender"]):
                thread.append(email["threadId"])
                new_emails.append({
                    "id": email["id"],
                    "subject": email["subject"],
                    "snippet": email["snippet"],
                    "threadId": email["threadId"]
                })
        checked_emails.extend([email["id"] for email in emails])

        return {
            **state,
            "checked_emails_ids": checked_emails,
            "emails": new_emails
        }
    
    def wait_next_run(self, state):
        print("Waiting for next run...")
        time.sleep(30)
        return state
    
    def new_email(self, state):
        if len(state["emails"]) == 0:
            print("No new emails found.")
            return "end"
        else:
            print("New emails found.")
            return "continue"