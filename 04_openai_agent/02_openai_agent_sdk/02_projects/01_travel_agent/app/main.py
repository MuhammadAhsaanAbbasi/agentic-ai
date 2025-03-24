import streamlit as st
import asyncio
import uuid
import json
from datetime import datetime
from typing import List, Dict, Any
import os

from services.agnets import (
    travel_agent, UserContext, TravelPlan, FlightRecommendation, HotelRecommendation
)
from agents import Runner

# Page Configuration
st.set_page_config(
    page_title="Travel Agent",
    page_icon="🛫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better markdown
st.markdown("""
<style>
    .chat-message {
        padding: 1.5rem; 
        border-radius: 0.5rem; 
        margin-bottom: 1rem; 
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #e6f7ff;
        border-left: 5px solid #2196F3;
    }
    .chat-message.assistant {
        background-color: #f0f0f0;
        border-left: 5px solid #4CAF50;
    }
    .chat-message .content {
        display: flex;
        margin-top: 0.5rem;
    }
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 1rem;
    }
    .message {
        flex: 1;
        color: #000000;
    }
    .timestamp {
        font-size: 0.8rem;
        color: #888;
        margin-top: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for chat history, thread id, user context, and processing message
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "user_context" not in st.session_state:
    st.session_state.user_context = UserContext(user_id=str(uuid.uuid4()))

if "processing_message" not in st.session_state:
    st.session_state.processing_message = None

# Function to format agent responses based on output type
def format_agent_response(output):
    if hasattr(output, "model_dump"):
        output = output.model_dump()
    
    if isinstance(output, dict):
        # Structured output for travel plan
        if "destination" in output:
            html = f"""
            <h3>Travel Plan for {output.get("destination", "Your Trip")}</h3>
            <p><strong>Duration:</strong> {output.get("duration_days", "N/A")} days</p>
            <p><strong>Budget:</strong> ${output.get("budget", "N/A")}</p>
            <h4>Recommended Activities:</h4>
            <ul>
            """
            for activity in output.get("activities", []):
                html += f"<li>{activity}</li>"
            html += "</ul>"
            html += f"""
            <h4>Notes:</h4>
            <p>{output.get("notes", "N/A")}</p>
            """
            return html

        # Flight recommendation
        elif "airline" in output:
            html = f"""
            <h3>Flight Recommendation</h3>
            <p><strong>Airline:</strong> {output.get("airline", "N/A")}</p>
            <p><strong>Departure Time:</strong> {output.get("departure_time", "N/A")}</p>
            <p><strong>Arrival Time:</strong> {output.get("arrival_time", "N/A")}</p>
            <p><strong>Price:</strong> ${output.get("price", "N/A")}</p>
            <p><strong>Direct Flight:</strong> {"Yes" if output.get("direct_flight", False) else "No"}</p>
            <p><strong>Recommendation Reason:</strong> {output.get("recommendation_reason", "N/A")}</p>
            """
            return html

        # Hotel recommendation
        elif "name" in output and "amenities" in output:
            html = f"""
            <h3>Hotel Recommendation</h3>
            <p><strong>Name:</strong> {output.get("name", "N/A")}</p>
            <p><strong>Location:</strong> {output.get("location", "N/A")}</p>
            <p><strong>Price Per Night:</strong> ${output.get("price_per_night", "N/A")}</p>
            <h4>Amenities</h4>
            <ul>
            """
            for amenity in output.get("amenities", []):
                html += f"<li>{amenity}</li>"
            html += "</ul>"
            html += f"""
            <p><strong>Recommendation Reason:</strong> {output.get("recommendation_reason", "N/A")}</p>
            """
            return html
    return str(output)

# Function to handle user input (appends user message to chat history)
def handle_user_message(user_input):
    timestamp = datetime.now().strftime("%I:%M %p")
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": timestamp,
    })

# Sidebar for user preferences
with st.sidebar:
    st.title("Travel Agent Preferences")
    st.subheader("About You")
    traveler_name = st.text_input("Traveler Name", value="Traveler")
    st.subheader("Travel Preferences")
    preferred_airlines = st.multiselect(
        "Preferred Airlines",
        ["Skyways", "OceanAir", "MountainJet", "Delta", "United", "American", "Southwest"],
        default=st.session_state.user_context.preferred_airlines
    )
    hotel_amenities = st.multiselect(
        "Must-Have Hotel Amenities",
        ["Wifi", "Pool", "Gym", "Free Breakfast", "Restaurant", "Spa", "Parking"],
        default=st.session_state.user_context.hotel_amenities
    )
    budget_level = st.select_slider(
        "Budget Level",
        options=["budget", "mid-range", "luxury"],
        value=st.session_state.user_context.budget_level or "mid-range",
    )
    if st.button("Save Preferences"):
        st.session_state.user_context.preferred_airlines = preferred_airlines
        st.session_state.user_context.hotel_amenities = hotel_amenities
        st.session_state.user_context.budget_level = budget_level
        st.success("Preferences saved successfully!")
    
    st.divider()
    if st.button("Start New Conversation"):
        st.session_state.chat_history = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.success("New conversation started!")

# Main Chat Interface
st.title("🛫 Travel Planner Assistant")
st.caption("Ask me about travel destinations, flight options, hotel recommendations, and more!")

# Display chat history
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(
            f"""
            <div class="chat-message user">
                <div class="content">
                    <img src="https://api.dicebear.com/7.x/avataaars/svg?seed={st.session_state.user_context.user_id}" class="avatar" />
                    <div class="message">
                        {message["content"]}
                        <div class="timestamp">
                        {message["timestamp"]}
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="chat-message assistant">
                <div class="content">
                    <img src="https://api.dicebear.com/7.x/bottts/svg?seed=travel-agent" class="avatar" />
                    <div class="message">
                        {message["content"]}
                        <div class="timestamp">{message["timestamp"]}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Use st.chat_input to get new user input
user_input = st.chat_input("Ask me anything about travel...")

# When a new message is entered, add it and set it for processing
if user_input:
    handle_user_message(user_input)
    st.session_state.processing_message = user_input
    st.rerun()
    # Don't call st.rerun() immediately so that we can process the message below

# Process the message if one is waiting
if st.session_state.processing_message:
    with st.spinner("Thinking about your plan..."):
        try:
            # Prepare the input for the agent; using full chat history if available.
            if len(st.session_state.chat_history) > 1:
                input_list = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.chat_history]
            else:
                input_list = st.session_state.processing_message

            # Run the agent asynchronously
            result = asyncio.run(Runner.run(
                travel_agent,
                input=input_list,
                context=st.session_state.user_context,
            ))

            response_content = format_agent_response(result.final_output)
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response_content,
                "timestamp": datetime.now().strftime("%I:%M %p"),
            })
        except Exception as e:
            error_message = f"Sorry, encountered an error: {str(e)}"
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": error_message,
                "timestamp": datetime.now().strftime("%I:%M %p"),
            })
            st.error(f"Error processing message: {e}")
        finally:
            # Clear the processing message so we don't process it again
            st.session_state.processing_message = None
            st.rerun()

# Footer
st.divider()
st.caption("Powered by OpenAI AGents SDK || Built with Streamlit")
