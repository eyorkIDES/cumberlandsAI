import streamlit as st
from openai import OpenAI
import time

# Assistant and Thread Configuration
assistant_id = "asst_YkgNKU6zP0LuzqwI9cAlP05t"
openai_api_key = st.secrets["DB_API_KEY"]

# Set tab name (title) and favicon
st.set_page_config(
    page_title="UC AI Assistant",  # This sets the tab name
    page_icon="favicon.png",  # This sets the favicon (must be a local file or URL)
)

# Create banner layout
col1, col2 = st.columns([1, 2])  # Adjust ratio for image and text

with col1:
    st.image("logo.webp", width=1500)  # Display image

st.title("AI Assistant")  # Assistant title

st.write("Ask anything to test the assistant's capabilities")  # Description text

# Password Authentication
placeholder = st.empty()  # Create a placeholder
# Display an element inside the placeholder
with placeholder:
    password = st.text_input("Password:", type="password")

if password != "patriots":
    st.info("Please enter password to access chatbot", icon="🗝️")
else:
    placeholder.empty()  # Remove the element
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
    if prompt := st.chat_input("How can I help?"):
        # Save user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Send user message to Assistant
        client.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=prompt
        )

        # Run assistant
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
        )

        # Reserve placeholder for assistant response
        assistant_placeholder = st.chat_message("assistant")
        response_container = assistant_placeholder.empty()

        with response_container:
            with st.spinner("Typing..."):
                # Poll until run is completed
                while True:
                    run_status = client.beta.threads.runs.retrieve(
                        thread_id=thread_id, run_id=run.id
                    )
                    if run_status.status == "completed":
                        break
                    time.sleep(2)

        # Retrieve the latest message
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        last_message = messages.data[0]
        text_obj = last_message.content[0].text
        raw_response = text_obj.value
        annotations = text_obj.annotations

        # Clean citations
        clean_response = raw_response
        references = ""
        for ann in annotations:
            if ann.type == "file_citation":
                clean_response = clean_response.replace(ann.text, "")
        for i, ann in enumerate(annotations):
            if ann.type == "file_citation":
                citation = ann.file_citation
                file_id = citation.file_id
                file_obj = client.files.retrieve(file_id)
                file_name = file_obj.filename
                references += f"[{i + 1}] {file_name}  \n"

        final_response = clean_response
        if references:
            final_response += "\n\nSource:\n" + references

        # Replace spinner with assistant message
        response_container.markdown(final_response)

        # Save assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": final_response})
