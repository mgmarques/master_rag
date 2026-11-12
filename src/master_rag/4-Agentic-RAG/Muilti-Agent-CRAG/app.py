import os

import openai
import streamlit as st
from dotenv import load_dotenv
from graph import query

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = API_KEY

st.write("Streamlit loves LLMs! 🤖 [Build your own chat app](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps) in minutes, then make it powerful by adding images, dataframes, or even input widgets to the chat.")
st.caption("Note that this demo app is connected to a local Ollama through the OpenAI API. You can change it to connect to any other LLM server;)")

st.title("🦜🔗 Advanced RAG Techniques Helper App")
chat_placeholder = st.empty()


def init_chat_history():
    """Initialize chat history with a system message."""
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
        st.session_state.messages = [
            {"role": "system", "content": "Let's start chatting! 👇"}
        ]


def start_chat():
    """Start the chatbot conversation."""
    # Display chat messages from history on app rerun
    with chat_placeholder.container():
        for message in st.session_state.messages:
            if message["role"] != "system":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response from Chat models
        # response = query(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            #st.markdown(response)
            # Generate response from Chat models
            response = st.write_stream(query(prompt))

        # Add assistant's response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    init_chat_history()
    start_chat()
