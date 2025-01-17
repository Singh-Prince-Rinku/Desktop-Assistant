import asyncio
from random import randint
from PIL import Image, UnidentifiedImageError
import requests
from dotenv import get_key
import os
from time import sleep

# Define constants
DATA_FOLDER = "Data"
FRONTEND_FILE_PATH = os.path.join(r'C:\Users\princ\OneDrive\Desktop Assistant\Frontent\Files\ImageGeneration.data')
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
HUGGINGFACE_API_KEY = get_key(".env", "HuggingFaceAPIKey")
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

# Ensure the data folder exists
os.makedirs(DATA_FOLDER, exist_ok=True)

def open_images(prompt):
    """Opens images generated based on the given prompt."""
    sanitized_prompt = prompt.replace(" ", "_")
    file_names = [f"{sanitized_prompt}{i}.jpg" for i in range(1, 8)]
    
    for file_name in file_names:
        image_path = os.path.join(DATA_FOLDER, file_name)
        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)
        except (IOError, UnidentifiedImageError):
            print(f"Error: {image_path} does not seem to be a valid image file.")

async def query(payload):
    """Sends a request to the HuggingFace API."""
    try:
        response = await asyncio.to_thread(requests.post, HUGGINGFACE_API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        if "image" not in response.headers.get("Content-Type", ""):
            print("Error: API did not return an image.")
            return None
        return response.content
    except requests.RequestException as e:
        print(f"Error during API request: {e}")
        return None

async def generate_image(prompt: str):
    """Generates images asynchronously based on the given prompt."""
    tasks = []
    sanitized_prompt = prompt.replace(" ", "_")

    for i in range(3):
        payload = {
            "inputs": f"{prompt}, quality=4k, sharpness=maximum, ultra high details, high resolution, seed={randint(0, 1000000)}"
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    image_bytes_list = await asyncio.gather(*tasks)

    # Save the images to files
    for i, image_bytes in enumerate(image_bytes_list):
        file_path = os.path.join(DATA_FOLDER, f"{sanitized_prompt}{i+1}.jpg")
        if image_bytes:
            try:
                with open(file_path, "wb") as f:
                    f.write(image_bytes)
                print(f"Image saved: {file_path}")
            except Exception as e:
                print(f"Error saving image {i+1}: {e}")
        else:
            print(f"Image {i+1} generation failed.")

def GenerateImages(prompt: str):
    """Wrapper function to generate images and open them."""
    asyncio.run(generate_image(prompt))
    open_images(prompt)

# Main loop to monitor ImageGeneration.data
while True:
    try:
        with open(FRONTEND_FILE_PATH, "r") as f:
            data = f.read()

        prompt, status = data.split(",")

        if status.strip() == "True":
            print("Generating Images...")
            GenerateImages(prompt=prompt.strip())

            # Update the status in ImageGeneration.data
            with open(FRONTEND_FILE_PATH, "w") as f:
                f.write(f"{prompt.strip()}, False")
            break
        else:
            sleep(1)
    except Exception as e:
        print(f"Error: {e}")
        sleep(1)
