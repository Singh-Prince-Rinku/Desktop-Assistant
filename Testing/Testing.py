from Frontent.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophonesStatus,
    AnswerModifier,
    QueryModifier,
    GetAssistantStatus,
    GetMicrophonesStatus
)

from Backend.Model import first_layer_dmm
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech

from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")
DefaultMessage = f'''{Username}: Hello {Assistantname}, How are You?
{Assistantname}: Welcome {Username}. I am doing well. How may I help you?'''

# Define global variables
subprocesses = []
Functions = ["open", "close", "play", "system", "contents", "google search", "youtube search"]

# Function to show default chat if no chats exist
def ShowDefaultChatIfNoChats():
    try:
        with open(r'Data\ChatLog.json', "r", encoding='utf8') as file:
            if len(file.read()) < 5:
                with open(TempDirectoryPath('Database.data'), "w", encoding='utf8') as db_file:
                    db_file.write("")
                with open(TempDirectoryPath('Responses.data'), "w", encoding='utf8') as resp_file:
                    resp_file.write(DefaultMessage)
    except FileNotFoundError:
        print("ChatLog.json not found.")
    except Exception as e:
        print(f"Error in ShowDefaultChatIfNoChats: {e}")

# Function to read chat logs
def ReadChatLogJson():
    try:
        with open(r'Data\ChatLog.json', "r", encoding='utf8') as file:
            return json.load(file)
    except FileNotFoundError:
        print("ChatLog.json not found.")
        return []
    except json.JSONDecodeError:
        print("Error decoding JSON from ChatLog.json.")
        return []

# Function to integrate chat logs into a database
def ChatLogIntegration():
    try:
        json_data = ReadChatLogJson()
        formatted_chatlog = ""
        for entry in json_data:
            if entry["role"] == "user":
                formatted_chatlog += f"User: {entry['content']}\n"
            elif entry["role"] == "assistant":
                formatted_chatlog += f"Assistantname: {entry['content']}\n"

        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write(AnswerModifier(formatted_chatlog))
    except Exception as e:
        print(f"Error in ChatLogIntegration: {e}")

# Function to show chats on GUI
def ShowChatsOnGUI():
    try:
        with open(TempDirectoryPath('Database.data'), 'r+', encoding='utf-8') as file:
            Data = file.read()
            if len(Data) > 0:
                lines = Data.split('\n')
                result = '\n'.join(lines)
                file.seek(0)
                file.write(result)
                file.truncate()
    except FileNotFoundError:
        print(f"Error: File {TempDirectoryPath('Database.data')} not found.")
    except Exception as e:
        print(f"Error in ShowChatsOnGUI: {e}")

# Function to initialize the system
def InitialExecution():
    SetMicrophonesStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

InitialExecution()

# Function to execute main tasks
def MainExecution():
    try:
        TaskExecution = False
        ImageExecution = False
        ImageGenerationQuery = ""

        SetAssistantStatus("Listening...")
        Query = SpeechRecognition()
        ShowTextToScreen(f"{Username}: {Query}")
        SetAssistantStatus("Thinking...")
        Decision = first_layer_dmm(Query)

        print(f"Decision: {Decision}")

        G = any(i.startswith("general") for i in Decision)
        R = any(i.startswith("realtime") for i in Decision)

        Merged_query = " and ".join(
            "".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")
        )

        for query in Decision:
            if "generate" in query:
                ImageGenerationQuery = str(query)
                ImageExecution = True

        for query in Decision:
            if not TaskExecution and any(query.startswith(func) for func in Functions):
                run(Automation(list(Decision)))
                TaskExecution = True

        if ImageExecution:
            with open(r"Frontent\Files\ImageGeneration.data", "w") as file:
                file.write(f"{ImageGenerationQuery}, True")

            try:
                p1 = subprocess.Popen(['python', r'Backend\ImageGeneration.py'],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    stdin=subprocess.PIPE, shell=False)
                subprocesses.append(p1)
            except Exception as e:
                print(f"Error Starting ImageGeneration.py: {e}")

        if G and R or R:
            SetAssistantStatus("Searching...")
            Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
            ShowTextToScreen(f"{Assistantname}: {Answer}")
            SetAssistantStatus("Answering...")
            TextToSpeech(Answer)
            return True

        else:
            for query in Decision:
                if "general" in query:
                    SetAssistantStatus("Thinking...")
                    QueryFinal = query.replace("general", " ")
                    Answer = ChatBot(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname}: {Answer}")
                    SetAssistantStatus("Answering...")
                    TextToSpeech(Answer)
                    return True

                elif "realtime" in query:
                    SetAssistantStatus("Searching...")
                    QueryFinal = query.replace("realtime", " ")
                    Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname}: {Answer}")
                    SetAssistantStatus("Answering...")
                    TextToSpeech(Answer)
                    return True

                elif "exit" in query:
                    QueryFinal = "Okay, Bye!"
                    Answer = ChatBot(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname}: {Answer}")
                    SetAssistantStatus("Answering...")
                    TextToSpeech(Answer)
                    os._exit(1)
    except Exception as e:
        print(f"Error in MainExecution: {e}")

# Thread to handle microphone input
def FirstThread():
    while True:
        try:
            CurrentStatus = GetMicrophonesStatus("status")
            if CurrentStatus == "True":
                MainExecution()
            else:
                AIStatus = GetAssistantStatus("status")
                if "Available" in AIStatus:
                    sleep(0.1)
                else:
                    SetAssistantStatus("Available...")
        except Exception as e:
            print(f"Error in FirstThread: {e}")

# Thread to handle the GUI
def SecondThread():
    try:
        GraphicalUserInterface()
    except Exception as e:
        print(f"Error in SecondThread: {e}")

# Main program execution
if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()
