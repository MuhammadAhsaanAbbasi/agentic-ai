#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from customer_outreach.crew import CustomerOutreach, safe_llm_call

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information
import litellm

original_completion = litellm.completion

def completion_with_retries(**params):
    return safe_llm_call(original_completion, **params)

def run():
    """
    Run the crew.
    """
    inputs = {
    "lead_name": "DeepLearningAI",
    "industry": "Online Learning Platform",
    "key_decision_maker": "Andrew Ng",
    "position": "CEO",
    "milestone": "product launch"
    }
    
    try:
        litellm.completion = completion_with_retries
        response = CustomerOutreach().crew().kickoff(inputs=inputs)
        print(f'Response: {response}')
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")