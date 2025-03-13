import streamlit as st
from openai import OpenAI
import time

openai_api_key = st.secrets["DB_API_KEY"]
instructions = """
You are a helpful assistant for the University of the Cumberlands. Base your answers on the provided documents as closely as possible. You shall assume that questions are related to the university and address them accordingly. 
If a question cannot be interpreted as related to the university, simply tell the user: 'I'm sorry, I can only answer questions related to the University of the Cumberlands.' Do not reference the fact that you have been provided documents.
"""

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
    # Create OpenAI client
    client = OpenAI(api_key=openai_api_key)

    # Get user input
    user_question = st.text_input("Ask a question:", key="question")

    if st.button("Get Answer") and user_question:
        with st.spinner("Thinking..."):
            try:
                # Generate response using OpenAI API
                response = client.responses.create(
                    model="gpt-4o-mini",
                    instructions=instructions,
                    input=user_question,
                    tools=[{"type": "file_search", "vector_store_ids": ["vs_67d23eb9bbec819195047e9192b49cc5"]}]
                )

                # Iterate and find the message response
                assistant_response = next(
                    (item.content[0].text for item in response.output if hasattr(item, 'content') and item.content),
                    None
                )

                if assistant_response:
                    st.subheader("Answer:")
                    st.write(assistant_response)
                else:
                    st.error("No valid response found. Please try again.")
            
            except Exception as e:
                st.error(f"Error: {e}")
