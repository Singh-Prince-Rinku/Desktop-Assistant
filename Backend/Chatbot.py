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

# Define the system message
System = f"""Hello, I am {Username}. You are an advanced AI chatbot named {Assistantname} with real-time up-to-date information from the internet.
*** Do not tell the time unless asked. Do not talk too much, just answer the question. ***
*** Reply only in English, even if the question is in Hindi. ***
*** Never mention your training data. ***
"""

SystemChatBot = [
    {"role": "system", "content": System}
]

# Load or initialize chat history
chat_log_path = r"Data\ChatLog.json"
try:
    with open(chat_log_path, "r") as f:
        message_history = load(f)
except FileNotFoundError:
    message_history = []

# Function to get real-time information
def RealtimeInformation():
    current_time = datetime.datetime.now()
    return f"Day: {current_time.strftime('%A')}, Date: {current_time.strftime('%d-%B-%Y')}, Time: {current_time.strftime('%H:%M:%S')}."

# Function to clean the chatbot's response
def AnswerModifier(answer):
    return '\n'.join(line.strip() for line in answer.split('\n') if line.strip())

# Chatbot function
def ChatBot(query):
    """Sends the user's query to the chatbot and returns the AI's response."""

    try:
        # Append user's message to history
        message_history.append({"role": "user", "content": query})

        # Call the Groq API
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",  
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + message_history,
            max_tokens=2048,
            temperature=0.7,  # Slight randomness for better responses
            top_p=0.9,
            stream=False
        )

        # Extract AI response
        answer = response.choices[0].message.content.strip()

        # Append AI response to history
        message_history.append({"role": "assistant", "content": answer})

        # Save updated chat history
        with open(chat_log_path, "w") as f:
            dump(message_history, f, indent=4)

        return AnswerModifier(answer)

    except Exception as e:
        print(f"Error: {e}")
        return f"An error occurred: {e}"

# Main chatbot loop
if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        print(ChatBot(user_input))
