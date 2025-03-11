#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from youtube_automation_crew.crew import YoutubeAutomationCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'video_topic': 'Build AI Agents that EVOLVE Over Time',
        'video_details': """One of the biggest advantages of building AI agents over traditional automations is that they are supposed to act more like a human. But for being so human, they sure have a pretty terrible memory most of the time.

        We want our agents to get smarter over time through interacting with us - remembering goals, instructions, corrections, our preferences, etc.

        This kind of long term memory is when you really start to take your agents to the next level of personalization and human like behavior. In this video, I’ll show you step by step how to build these self-learning AI agents using an open source Python library called Mem0 which is specifically built for this purpose.
"""
    }
    
    try:
        result = YoutubeAutomationCrew().crew().kickoff(inputs=inputs)
        print(f"Response: {result}")
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        YoutubeAutomationCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        YoutubeAutomationCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        YoutubeAutomationCrew().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
