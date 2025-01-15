import cohere
from rich import print
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
cohere_api_key = env_vars.get("CohereAPIKey")

if not cohere_api_key:
    raise ValueError("Cohere API key not found in .env file.")

# Initialize Cohere client
co = cohere.Client(api_key=cohere_api_key)

# Define the decision-making model preamble
preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad'
*** Do not answer any query, just decide what kind of query is given to you. ***
-> Respond with 'general ( query )' if a query can be answered by a llm model (conversational ai chatbot) and doesn't require any up to date information like if the query is 'who was akbar?' respond with 'general who was akbar?', if the query is 'how can i study more effectively?' respond with 'general how can i study more effectively?', etc.
-> Respond with 'realtime ( query )' if a query can not be answered by a llm model (because they don't have realtime data) and requires up to date information.
-> Respond with 'open (application name or website name)' if a query is asking to open any application like 'open facebook', 'open telegram', etc.
-> Respond with 'close (application name)' if a query is asking to close any application like 'close notepad', 'close facebook', etc.
-> Respond with 'play (song name)' if a query is asking to play any song like 'play afsanay by ys', etc.
-> Respond with 'generate image (image prompt)' if a query is requesting to generate a image with given prompt like 'generate image of a lion', etc.
-> Respond with 'reminder (datetime with message)' if a query is requesting to set a reminder like 'set a reminder at 9:00pm on 25th june for my business meeting.'
-> Respond with 'system (task name)' if a query is asking to mute, unmute, volume up, volume down , etc.
-> Respond with 'content (topic)' if a query is asking to write any type of content like application, codes, emails or anything else about a specific topic.
-> Respond with 'google search (topic)' if a query is asking to search a specific topic on google.
-> Respond with 'youtube search (topic)' if a query is asking to search a specific topic on youtube.
*** If the query is asking to perform multiple tasks, respond with all the tasks in order. ***
*** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. ***
"""

# Available functions for classification
funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "remainder"
]

# Chat history
chat_history = [
    {"role": "user", "message": "how are you"},
    {"role": "chatbot", "message": "general how are you"},
    {"role": "user", "message": "do you like pizza?"},
    {"role": "chatbot", "message": "general do you like pizza"},
    {"role": "user", "message": "open chrome and tell me about tony stark"},
    {"role": "chatbot", "message": "open chrome, general tell me about tony stark"},
]

# Function to process user input and classify the query
def first_layer_dmm(prompt: str):
    messages = [{"role": "user", "content": prompt}]
    
    try:
        # Call Cohere chat API
        response = co.chat(
            model="command-r-plus",
            message=prompt,
            temperature=0.7,
            chat_history=chat_history,
            preamble=preamble
        )

        # Extract the response
        response_text = response.text.strip()
        response_text = response_text.replace("\n", " ")
        tasks = [task.strip() for task in response_text.split(",")]

        # Filter valid tasks
        filtered_tasks = [task for task in tasks if any(task.startswith(func) for func in funcs)]

        if "(query)" in " ".join(filtered_tasks):
            # Retry if the query is ambiguous
            print("[yellow]Ambiguous query detected. Retrying...[/yellow]")
            return first_layer_dmm(prompt=prompt)
        
        return filtered_tasks

    except Exception as e:
        print(f"[red]Error occurred: {e}[/red]")
        return []

# Main function
if __name__ == "__main__":
    print("[bold green]Decision-Making Model[/bold green]")
    while True:
        user_input = input(">>> ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("[bold blue]Goodbye![/bold blue]")
            break
        result = first_layer_dmm(user_input)
        print(f"[bold cyan]Response:[/bold cyan] {result}")
