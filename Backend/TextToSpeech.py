import pygame
import random
import asyncio
import os
from dotenv import dotenv_values
import edge_tts  # Ensure edge_tts is installed: pip install edge_tts

# Load environment variables
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice")
if not AssistantVoice:
    raise ValueError("AssistantVoice not found in .env file!")

# Cross-platform file path
file_path = os.path.join("Data", "speech.mp3")

async def TextToAudioFile(text: str) -> None:
    """Convert text to an audio file using edge_tts."""
    if os.path.exists(file_path):
        os.remove(file_path)

    communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')
    await communicate.save(file_path)

def TTS(text: str, func=lambda r=None: True) -> bool:
    """Text-to-speech function with pygame."""
    try:
        asyncio.run(TextToAudioFile(text))
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            if not func():
                break
            pygame.time.Clock().tick(10)
        return True

    except Exception as e:
        print(f"Error in TTS: {e}")
        return False

    finally:
        try:
            func(False)
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception as e:
            print(f"Error in finally block: {e}")

def TextToSpeech(text: str, func=lambda r=None: True):
    """Handle text and decide whether to split or play fully."""
    sentences = text.split(".")
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
    ]

    if len(sentences) > 10 and len(text) >= 2500:
        TTS(" ".join(sentences[:2]) + "." + random.choice(responses), func)
    else:
        TTS(text, func)

if __name__ == "__main__":
    while True:
        try:
            text = input("Enter the text: ")
            TextToSpeech(text)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
