import streamlit as st
from openai import OpenAI
import time

# Assistant and Thread Configuration
assistant_id = "asst_YkgNKU6zP0LuzqwI9cAlP05t"

# Show title and description.
st.title("💬 UC AI Assistant")
st.write("Ask anything to test the assistant's capabilities")

# Ask user for their OpenAI API key
openai_api_key = st.secrets["DB_API_KEY"]
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create an OpenAI client
    client = OpenAI(api_key=openai_api_key)

    # Ensure we have a thread ID in session state
    if "thread_id" not in st.session_state:
        thread = client.beta.threads.create()  # Create a new thread
        st.session_state.thread_id = thread.id

    thread_id = st.session_state.thread_id

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input for user
    if prompt := st.chat_input("What is up?"):
        # Store user message in chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Send message to OpenAI Assistant Thread
        client.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=prompt
        )

        # Run the assistant
        run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)

        # Polling loop: Wait for completion
        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            if run_status.status == "completed":
                break
            time.sleep(2)  # Wait before checking again

        # Retrieve assistant response
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        last_message = messages.data[0]  # Get the latest assistant message
        response = last_message.content[0].text.value

        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response)

        # Store assistant response in chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
