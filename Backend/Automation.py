from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os

# Load environment variables from .env file
env_vars = dotenv_values(".env")

# Fetch the API key
GroqAPIkey = env_vars.get("GROQ_API_KEY")

# Set the environment variable for the Groq client
if GroqAPIkey:
    os.environ["GROQ_API_KEY"] = GroqAPIkey  # Explicitly set as global variable
else:
    raise ValueError("GROQ_API_KEY is not set in the .env file. Please provide a valid API key.")

# Initialize Groq client
client = Groq(api_key=os.environ["GROQ_API_KEY"])

# CSS classes for parsing HTML (update as needed)
classes = [
    "zCubwf", "hgKElc", "LTKOO sY7ric", "ZOLcW",
    "“gsrt vk_bk FzvWSb YwPhnf", "pclqee", "tw-Data-text tw-text-small tw-ta",
    "IZ6rdc", "O5uR6d LTKOO", "“vlzY6d", "“webanswers-webanswers_table_webanswers-table",
    "“dDoNo ikb4Bb gsrt", "sXLa0e", "LwkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"
]

# User agent for web requests
useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.265 Safari/537.36"

# Response template
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask."
]
message = []

# System prompt for AI content
SystemChatBot = [
    {"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'Assistant')}, You are a content writer. You have to write like a letter."}
]

# Define functions
def GoogleSearch(topic):
    search(topic)
    return True

def Content(topic):
    def OpenNotepad(file):
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor, file])

    def ContentWriteAI(prompt):
        message.append({"role": "user", "content": f"{prompt}"})
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + message,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content
        answer = answer.replace("</s>", "")
        message.append({"role": "assistant", "content": answer})
        return answer

    topic = topic.replace("Content", "").strip()
    content_by_ai = ContentWriteAI(topic)

    os.makedirs("Data", exist_ok=True)
    file_path = os.path.join("Data", f"{topic.lower().replace(' ', '')}.txt")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content_by_ai)

    OpenNotepad(file_path)

def YoutubeSearch(topic):
    url_for_search = f"https://www.youtube.com/results?search_query={topic}"
    webbrowser.open(url_for_search)
    return True

def PlayYoutube(query):
    playonyt(query)
    return True


def OpenApp(app, sess=requests.Session()):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        def extract_link(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': 'UWckNb'})
            return [link.get('href') for link in links]

        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": useragent}
            response = sess.get(url, headers=headers)
            if response.status_code == 200:
                return response.text
            else:
                print("Failed to retrieve search results...")
            return None

        html = search_google(app)
        if html:
            link = extract_link(html)[0]
            webopen(link)
        return True

def CloseApp(app):
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception as e:
        print(f"Error closing app: {e}")
        return False

def System(command):
    def mute():
        keyboard.press_and_release("volume mute")

    def unmute():
        keyboard.press_and_release("volume unmute")

    def volume_up():
        keyboard.press_and_release("volume up")

    def volume_down():
        keyboard.press_and_release("volume down")

    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()
    return True

async def TranslateAndExecute(commands: list[str]):
    funcs = []
    for command in commands:
        if command.startswith("open"):
            fun = asyncio.to_thread(OpenApp, command.removeprefix("open").strip())
            funcs.append(fun)
        elif command.startswith("close"):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close").strip())
            funcs.append(fun)
        elif command.startswith("play"):
            fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play").strip())
            funcs.append(fun)
        elif command.startswith("content"):
            fun = asyncio.to_thread(Content, command.removeprefix("content").strip())
            funcs.append(fun)
        elif command.startswith("google search"):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search").strip())
            funcs.append(fun)
        elif command.startswith("youtube search"):
            fun = asyncio.to_thread(YoutubeSearch, command.removeprefix("youtube search").strip())
            funcs.append(fun)
        elif command.startswith("system"):
            fun = asyncio.to_thread(System, command.removeprefix("system").strip())
            funcs.append(fun)
        else:
            print(f"Unknown command: {command}")

    results = await asyncio.gather(*funcs)
    for result in results:
        yield result

async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True
