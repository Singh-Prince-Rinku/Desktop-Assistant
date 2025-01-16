from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize the Groq client
client = Groq(api_key=GroqAPIKey)

message = []

# Define the system message
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [
    {"role": "system", "content": System}
]

# Load existing chat log or create a new one
try:
    with open(r"Data\ChatLog.json", "r") as f:
        message = load(f)
except FileNotFoundError:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

# Get real-time information
def RealtimeInformation():
    current_data_time = datetime.datetime.now()
    day = current_data_time.strftime("%A")
    date = current_data_time.strftime("%d")
    month = current_data_time.strftime("%B")
    year = current_data_time.strftime("%Y")
    hour = current_data_time.strftime("%H")
    minute = current_data_time.strftime("%M")
    second = current_data_time.strftime("%S")
    
    data = f"please use this real-time information if needed,\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours : {minute} minutes : {second} seconds.\n"
    return data

# Format the chatbot's answer
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

# Main chatbot function
def ChatBot(Query):
    """This function sends the user's query to the chatbot and returns the AI's response."""
    
    try:
        # Load chat log
        with open(r"Data\ChatLog.json", "r") as f:
            message = load(f)
        
        # Add the user's query
        message.append({
            "role": "user",
            "content": Query
        })
        
        # Ensure the model you are using is available and correct
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # This is a commonly used valid model for many APIs.
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + message,
            max_tokens=2048,
            temperature=0.5,
            top_p=0.9,
            stream=False
        )
        
        # Get the AI's response
        Answer = completion.choices[0].message.content
        
        # Append the AI's response to the chat log
        message.append({
            "role": "assistant",  
            "content": Answer
        })
        
        # Save updated chat log
        with open(r"Data\ChatLog.json", "w") as f:
            dump(message, f, indent=4)
        
        return AnswerModifier(Answer)
    
    except Exception as e:
        # Handle errors and reset chat log if needed
        print(f"Error occurred: {e}")
        with open(r"Data\ChatLog.json", "w") as f:
            dump([], f, indent=4)
        return f"An error occurred: {e}"

# Main program loop
if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")
        print(ChatBot(user_input))
