from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

# Load environment variables from .env file
env_vars = dotenv_values(".env")
Username = env_vars["Username"]
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# Define system message
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# Initialize chat log
try:
    with open(r"Data\ChatLog.json", "r") as f:
        message = load(f)
except:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

# Function to perform Google search
def GoogleSearch(query):
    # Perform the Google search and get a list of URLs
    results = list(search(query, num_results=5))
    Answer = f"The search results for '{query}' are:\n[Start]\n"
    
    for i in results:
        Answer += f"URL: {i}\n\n"  # Now only appending the URL instead of non-existent 'title' and 'description'
    
    Answer += "[end]"
    return Answer

# Function to clean up the answer format
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

# Initialize System and Chatbot messages
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, How can I help you?"}
]

# Function to return real-time information
def Information():
    data = ""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    
    data += f"Use this real-time Information if needed:\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours, {minute} minutes, {second} seconds.\n"
    return data

# Function to interact with the system and retrieve answers
def RealtimeSearchEngine(prompt):
    global SystemChatBot, message
    
    # Load the previous chat log
    with open(r"Data\ChatLog.json", "r") as f:
        message = load(f)
    
    # Add the user's prompt to the message history
    message.append({"role": "user", "content": f"{prompt}"})
    
    # Append Google search results to the system message
    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})
    
    # Ensure that all messages are in the correct format
    # Now the message format is properly set with valid 'role' values (system, user, assistant)
    completion = client.chat.completions.create(
        model="gemma2-9b-it", 
        messages=SystemChatBot + [{"role": "system", "content": Information()}] + message,
        max_tokens=2048,
        temperature=0.7,
        top_p=1,
        stream=True,
        stop=None
    )
    
    # Collect the model's response
    Answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content
    
    # Clean up the answer and remove any unwanted formatting
    Answer = Answer.strip().replace("</s>", "")
    message.append({"role": "assistant", "content": Answer})
    
    # Save the updated chat log
    with open(r"Data\ChatLog.json", "w") as f:
        dump(message, f, indent=4)
    
    # Remove the last system message (Google search results)
    SystemChatBot.pop()
    
    return AnswerModifier(Answer=Answer)

# Main loop to take user input and generate responses
if __name__ == "__main__":
    while True:
        prompt = input("Enter Your Query: ")
        print(RealtimeSearchEngine(prompt))
