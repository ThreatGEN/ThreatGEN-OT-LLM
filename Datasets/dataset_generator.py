# This script uses the OpenAI Assistants API to create a security analyst assistant that can help create LLM training/fine tuning datasets from cybersecurity standards, documents, LLM training data, and more. The assistant will be asked to create as many question and answer sets from the data that it can and provide at least 100 sets. The assistant will then be run and the responses will be extracted and and put in the proper JSON format for LLM fine tuning ingestion. You do need a ChatGPT Plus account or pre-paid credits.

import openai
from openai import OpenAI
import time
import os

# Set the OpenAI API key
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Initialize the OpenAI client
client = OpenAI()

# Upload a file to use for the assistant
file = client.files.create(
  file=open("data.txt", "rb"), # Change the file name (data.txt) as needed
  purpose='assistants'
)

# Function to create a security analyst assistant
security_analyst_assistant = client.beta.assistants.create(
    name="OT Cybersecurity Analyst Assistant",
    instructions="You are an OT cybersecurity analyst that can help create LLM training datasets from cybersecurity standards, documents, your own knowledge, and more",
    model="gpt-4-turbo-preview",
    tools=[{"type": "retrieval"}],
    file_ids=[file.id],
)

thread = client.beta.threads.create()

# Start the thread
message = client.beta.threads.messages.create(
    thread.id,
    role="user",
    content="Create as manyquestion and answer sets from the data that you can. Provide at least 100 sets."
)

message_id = message.id

# Run the thread
run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=security_analyst_assistant.id,
)

def get_run_response(run_id, thread_id):
    # Poll the run status in intervals until it is completed
    while True:
        run_status = client.beta.threads.runs.retrieve(run_id=run_id, thread_id=thread_id)
        if run_status.status == "completed":
            break
        time.sleep(5)  # Wait for 5 seconds before checking the status again

    # Once the run is completed, retrieve the messages from the thread
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    
    # Filter the messages by the role of 'assistant' to get the responses
    responses = [message for message in messages.data if message.role == "assistant"]
    
    # Extracting values from the responses
    values = []
    for response in responses:
        for content_item in response.content:  # Assuming 'content' is directly accessible within 'response'
            if content_item.type == 'text':  # Assuming each 'content_item' has a 'type' attribute
                values.append(content_item.text.value)  # Assuming 'text' object contains 'value'
    
    return values

# Retrieve the values from the run responses
values = get_run_response(run.id, thread.id)

# Print the extracted values
for value in values:
    print(value)