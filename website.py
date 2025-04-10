import streamlit as st
from openai import OpenAI
import time

# --- Config ---
assistant_id = "asst_YkgNKU6zP0LuzqwI9cAlP05t"
openai_api_key = st.secrets["DB_API_KEY"]

# --- Streamlit Page Setup ---
st.set_page_config(
    page_title="UC AI Assistant",
    page_icon="favicon.png",
)

# --- Header with Logo ---
col1, col2 = st.columns([1, 2])
with col1:
    st.image("logo.webp", width=1500)
st.title("AI Assistant")
st.write("Ask anything to test the assistant's capabilities")

# --- Password Protection ---
placeholder = st.empty()
with placeholder:
    password = st.text_input("Password:", type="password")

if password != "patriots":
    st.info("Please enter password to access chatbot")
    st.stop()
else:
    placeholder.empty()

# --- Initialize OpenAI Client ---
client = OpenAI(api_key=openai_api_key)

# --- Session Setup ---
if "thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input ---
if prompt := st.chat_input("How can I help?"):
    # Show user's message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add message to thread
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=prompt,
    )

    # Placeholder for assistant response
    with st.chat_message("assistant"):
        stream_area = st.empty()
        full_response = ""

        # Start assistant run with streaming
        stream = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
            stream=True,
        )

        annotations = []
        for event in stream:
            if event.event == "thread.message.delta":
                delta = event.data.delta
                if delta.content and len(delta.content) > 0:
                    part = delta.content[0].text.value
                    full_response += part
                    stream_area.markdown(full_response)
                if delta.content and delta.content[0].text.annotations:
                    annotations.extend(delta.content[0].text.annotations)

        # Clean Response
        clean_response = full_response
        references = ""
        for ann in annotations:
            if ann.type == "file_citation":
                clean_response = clean_response.replace(ann.text, "")

        # Add Sources
        seen_files = set()
        for i, ann in enumerate(annotations):
            if ann.type == "file_citation":
                citation = ann.file_citation
                if citation.file_id not in seen_files:
                    file_obj = client.files.retrieve(citation.file_id)
                    references += f"[{len(seen_files) + 1}] {file_obj.filename}  \n"
                    seen_files.add(citation.file_id)
        final_response = clean_response
        if references:
            final_response += "\n\nSource: \n" + references

        # Update stream area with cleaned output
        stream_area.markdown(final_response)

        # Save to history
        st.session_state.messages.append({
            "role": "assistant",
            "content": final_response
        })