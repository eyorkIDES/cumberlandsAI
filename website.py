import streamlit as st
import openai
import time


# website.py
# Ethan York
# Innovative Deisng and Engineering Solutions
# 1/25/2024

# Definitions
assistant_id = "asst_YkgNKU6zP0LuzqwI9cAlP05t"
thread_id= "thread_GB0cRlO0yillJVcYCxpL3uxj"
client = openai.OpenAI(api_key="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")
# If a question cannot be related to the university, respond with: 'I can only assist with topics related to the University of the Cumberlands.'

def wait_for_run_completion(client, thread_id, run_id, sleep_interval=5):
    """
    Waits for a run to complete and prints the elapsed time.:param client: The OpenAI client object.
    :param thread_id: The ID of the thread.
    :param run_id: The ID of the run.
    :param sleep_interval: Time in seconds to wait between checks.
    """
    while True:
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run.completed_at:
                elapsed_time = run.completed_at - run.created_at
                formatted_elapsed_time = time.strftime(
                    "%H:%M:%S", time.gmtime(elapsed_time)
                )
                print(f"Run completed in {formatted_elapsed_time}")
                st.write(f"Run completed in {formatted_elapsed_time}")
                # Get messages here once Run is completed!
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                last_message = messages.data[0]
                response = last_message.content[0].text.value
                print(f"Assistant Response: {response}")
                st.write(f"Assistant Response: {response}")
                break
        except Exception as e:
            break
        time.sleep(sleep_interval)


def send_message(message):
    message = client.beta.threads.messages.create(
        thread_id=thread_id, role="user", content=message
    )

    # == Run the Assistant
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions="",
    )

    # == Run it
    wait_for_run_completion(client=client, thread_id=thread_id, run_id=run.id)

# Title
st.title("UC Chatbot Test Environment")
st.write(thread_id)

# Simple text input
message = st.text_input("Prompt:")

# When the button is clicked...
if st.button("Submit"):
    send_message(message)