import streamlit as st

# Title
st.title("Hello, Streamlit!")

# Simple text input
user_name = st.text_input("Enter your name")

# When the button is clicked...
if st.button("Say Hello"):
    st.write(f"Hello, {user_name}!")
