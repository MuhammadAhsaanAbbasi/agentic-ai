#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from automate_event_planning.crew import AutomateEventPlanning, safe_llm_call

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
import litellm

original_completion = litellm.completion

def completion_with_retries(**params):
    return safe_llm_call(original_completion, **params)

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
    'event_topic': "Tech Innovation Conference",
    'event_description': "A gathering of tech innovators "
                         "and industry leaders "
                         "to explore future technologies.",
    'event_city': "San Francisco",
    'tentative_date': "2025-03-15", # Adjust date accooding yo your's time & date
    'expected_participants': 500,
    'budget': 20000,
    'venue_type': "Banquet/Conference Hall"
}
    
    try:
        # litellm.completion = completion_with_retries
        response=AutomateEventPlanning().crew().kickoff(inputs=inputs)
        print(f'Response: {response}')
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")