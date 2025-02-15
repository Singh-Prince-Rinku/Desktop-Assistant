import pygame
import random
import asyncio
import os
import re
from dotenv import dotenv_values
import edge_tts  # Ensure edge_tts is installed: pip install edge_tts

# Load environment variables
env_vars = dotenv_values(".env")
PreferredVoice = env_vars.get("PreferredVoice", "hi-IN-SwaraNeural")  # Use an Indian female voice

# Validate voice
valid_voices = {"hi-IN-SwaraNeural", "hi-IN-MadhurNeural"}  # Update with actual valid Indian female voices
if PreferredVoice not in valid_voices:
    raise ValueError("Invalid preferred voice specified in .env file!")

# Cross-platform file path
file_path = os.path.join("Data", "Speech1.mp3")

def detect_language(text: str) -> str:
    """Detect if the text is in Hindi or English."""
    hindi_pattern = re.compile("[\u0900-\u097F]+")
    return "hindi" if hindi_pattern.search(text) else "english"

async def TextToAudioFile(text: str) -> None:
    """Convert text to an audio file using edge_tts with the preferred Indian female voice."""
    if os.path.exists(file_path):
        os.remove(file_path)

    communicate = edge_tts.Communicate(text, PreferredVoice, pitch='+5Hz', rate='+13%')
    await communicate.save(file_path)

def TTS(text: str, func=lambda r=None: True) -> bool:
    """Text-to-speech function with pygame, supporting automatic language detection."""
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
    """Handle text and decide whether to split or play fully, supporting automatic language detection."""
    sentences = text.split(".")
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out.",
        "You can see the rest of the text on the chat screen.",
        "The remaining part of the text is now on the chat screen.",
        "बाकी का परिणाम चैट स्क्रीन पर छपा है, कृपया इसे देखें।",
        "आप शेष पाठ को चैट स्क्रीन पर देख सकते हैं।",
        "पाठ का शेष भाग अब चैट स्क्रीन पर है।",
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
