import streamlit as st
import asyncio
from autogen import ConversableAgent

# Streamlit app setup
st.title("Conversational AI Agent - Teacher")

class TrackableConversableAgent(ConversableAgent):
    def _process_received_message(self, message, sender, silent):
        if isinstance(message, dict) and "content" in message:
            with st.chat_message(sender.name):
                st.markdown(message["content"])
        else:
            st.error("Unexpected message format.")
        return super()._process_received_message(message, sender, silent)

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter your API key for gemini-1.5-flash:", type="password")
    subject = st.text_input("Enter the subject name (e.g., Mathematics):", "Mathematics")
    topic = st.text_input("Enter the topic name (e.g., Number System):", "Number System")
    level = st.text_input("Enter the level (e.g., Class 10th):", "Class 10th")
    output_type = st.selectbox(
        "Select the type of output you want:",
        ["Theory", "Solved Subjective Questions", "Solved MCQ type questions", 
         "Practice Subjective Questions", "Practice MCQ type questions"]
    )

# Ensure all required inputs are provided
if not api_key:
    st.warning("Please enter your API key.")
    st.stop()

# Create the configuration list for Gemini
config_list_gemini = [
    {
        "model": "gemini-1.5-flash",
        "api_key": api_key,
        "api_type": "google"
    }
]

# Initialize the agent_as_teacher
agent_as_teacher = TrackableConversableAgent(
    "Teacher",
    system_message=f"You are a {subject} teacher of {topic} for {level}. "
                   f"Your task is to answer everything related to {topic} asked by me. "
                   f"If I ask to provide {output_type.lower()} about that topic, then provide the {output_type.lower()} without compromising the quality.",
    llm_config={"config_list": config_list_gemini},
    is_termination_msg=lambda msg: "Thank You" in msg["content"],
    human_input_mode="NEVER",
)

# Initialize the student_proxy agent
student_proxy = TrackableConversableAgent(
    "human_proxy",
    llm_config=False,  # no LLM used for human proxy
    human_input_mode="ALWAYS",  # always ask for human input
)

# Input box for user question
user_input = st.chat_input("Ask a question to the agent:")
if user_input:
    async def initiate_chat():
        await student_proxy.a_initiate_chat(
            agent_as_teacher,
            message=user_input,
        )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(initiate_chat())
