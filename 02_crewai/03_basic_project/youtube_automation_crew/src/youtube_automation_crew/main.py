#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from youtube_automation_crew.crew import YoutubeAutomationCrew
import streamlit as st

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run(video_topic, video_details):
    """
    Run the crew.
    """
    inputs = {
        'video_topic': video_topic,
        'video_details': video_details
    }
    
    try:
        result = YoutubeAutomationCrew().crew().kickoff(inputs=inputs)
        print(f"Response: {result}")
        response = result.model_dump()
        return {
            "response": response["raw"],
            "answer" : response
            }
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


# def train():
#     """
#     Train the crew for a given number of iterations.
#     """
#     inputs = {
#         "topic": "AI LLMs"
#     }
#     try:
#         YoutubeAutomationCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

#     except Exception as e:
#         raise Exception(f"An error occurred while training the crew: {e}")

# def replay():
#     """
#     Replay the crew execution from a specific task.
#     """
#     try:
#         YoutubeAutomationCrew().crew().replay(task_id=sys.argv[1])

#     except Exception as e:
#         raise Exception(f"An error occurred while replaying the crew: {e}")

# def test():
#     """
#     Test the crew execution and returns the results.
#     """
#     inputs = {
#         "topic": "AI LLMs"
#     }
#     try:
#         YoutubeAutomationCrew().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

#     except Exception as e:
#         raise Exception(f"An error occurred while testing the crew: {e}")

st.set_page_config(page_title="YouTube Automation", page_icon="🎬" , layout="wide")

st.title("🎬 YouTube Automation Crew: AI-Powered Video Optimization")
st.write("🚀 Automate YouTube content research, title creation, description writing, and email marketing with an AI-driven Crew, ensuring maximum engagement and growth.")

video_topic = st.text_input("Enter the video topic:")
video_details = st.text_area("Enter the video details:")

if st.button("Optimize Video"):
    if video_topic and video_details:
        with st.spinner("Optimizing your video..."):
            try:
                result = run(video_topic, video_details)
                st.success("Video generated successfully!")
                st.markdown(result["response"])
                st.write(result["answer"])
            except Exception as e:
                st.error(f"An error occurred while generating the video: {e}")
    else:
        st.warning("Please enter both video topic and video details.")