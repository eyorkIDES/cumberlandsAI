# website.py
# Ethan York, Jon Hurd
# Innovative Design and Engineering Solutions
# 7/9/2025

import streamlit as st
from openai import OpenAI

# -----------------#
# CONFIGURATION   
# -----------------#

# Hard-code the ID of the pre-configured assistant
assistant_id = "asst_YkgNKU6zP0LuzqwI9cAlP05t"
# Retrieve OpenAI API key from Streamlit secrets store
openai_api_key = st.secrets["DB_API_KEY"]
# Set browser tab title and favicon
st.set_page_config(page_title="UC AI Assistant", page_icon="favicon.png")

# -----------------#
# HEADER BLOCK   
# -----------------#

# Define header visuals
col1, col2 = st.columns([1, 2])
with col1:
    st.image("logo.webp", width=1500)
st.title("AI Assistant")

# -----------------#
# PASSWORD ENTRY   
# -----------------#

# Password entry logic and display
placeholder = st.empty()
with placeholder:
    password = st.text_input("Password:", type="password")

# Hard-code password
if password != "patriots":
    st.info("Please enter password to access chatbot")
    # Stop generating page if incorrect password is entered
    st.stop()
else:
    placeholder.empty()
    st.caption("ℹ️ ChatBot can make mistakes. Please refer to official university channels for confirmation.")

# ----------------------#
# OPENAI INITIALIZATION   
# ----------------------#

# Define client with API key
client = OpenAI(api_key=openai_api_key)
# If not already defined, create a new thread
if "thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    # add session ID to streamlit session state
    st.session_state.thread_id = thread.id

# ----------------------#
# WEBSITE INITILIZATION 
# ----------------------#

# define "messages" structure to hold chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------#
# USER INPUT COLLECTION
# -----------------------#

# Chat Input
if prompt := st.chat_input("How can I help?"):
    # Show user's message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add message to thread
    client.beta.threads.messages.create(thread_id=st.session_state.thread_id, role="user", content=prompt)

    # Placeholder for assistant response
    with st.chat_message("assistant"):
        stream_area = st.empty()
        full_response = ""

        # --------------------------#
        # STREAM ASSISTANT RESPONSE
        # --------------------------#
        
        # Start a run and retrieve output incrementally
        stream = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
            stream=True,
        )
        
        # Loop through streamed events
        annotations = []
        for event in stream:
            if event.event == "thread.message.delta":
                delta = event.data.delta
                # Only proceed if there is actual content in this delta
                if delta.content and len(delta.content) > 0:
                    part = delta.content[0].text.value
                    full_response += part
                    stream_area.markdown(full_response)
                # Check for annotations and store them for later processing
                if delta.content and delta.content[0].text.annotations:
                    annotations.extend(delta.content[0].text.annotations)

        # --------------------------#
        # RESPONSE POST-PROCESSING
        # --------------------------#

        clean_response = full_response # Initialize clean response with whole response
        references = "" # Initialize a string to hold references

        # Loop through each annotation
        for ann in annotations:
            if ann.type == "file_citation":
                # Remove annotation from the response
                clean_response = clean_response.replace(ann.text, "")

        # Append formatted source references to the end
        seen_files = set()
        for i, ann in enumerate(annotations):
            if ann.type == "file_citation":
                citation = ann.file_citation
                # If not a duplicate reference, append to response
                if citation.file_id not in seen_files:
                    file_obj = client.files.retrieve(citation.file_id)
                    references += f"[{len(seen_files) + 1}] {file_obj.filename}  \n"
                    seen_files.add(citation.file_id)

        # Merge clean output with reference list            
        final_response = clean_response
        if references:
            final_response += "\n\nSource: \n" + references

        # Update stream area with cleaned output
        stream_area.markdown(final_response)

        # Store assistant message in conversation history
        st.session_state.messages.append({
            "role": "assistant",
            "content": final_response
        })
