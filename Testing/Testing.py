import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from time import sleep

# Constants
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
DATA_FOLDER = "Data"
STATUS_FILE = r"Frontend\Files\ImageGeneration.data"  # Relative path
HEADERS = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}

# Ensure the data folder exists
os.makedirs(DATA_FOLDER, exist_ok=True)

def open_images(prompt):
    """Open images based on the prompt."""
    sanitized_prompt = prompt.replace(" ", "_")
    files = [f"{sanitized_prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in files:
        image_path = os.path.join(DATA_FOLDER, jpg_file)
        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)
        except IOError:
            print(f"Error: {image_path} does not seem to be a valid image file")

async def query(payload):
    """Send API request and return the response."""
    try:
        response = await asyncio.to_thread(requests.post, API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error in API request: {e}")
        return None

async def generate_image(prompt):
    """Generate images asynchronously using the API."""
    tasks = []
    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4k, Sharpness=maximum, Ultra High Details, high resolution, seed={randint(0, 1000000)}"
        }
        tasks.append(asyncio.create_task(query(payload)))

    # Gather results
    image_bytes_list = await asyncio.gather(*tasks)
    sanitized_prompt = prompt.replace(" ", "_")

    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            file_path = os.path.join(DATA_FOLDER, f"{sanitized_prompt}{i + 1}.jpg")
            with open(file_path, "wb") as f:
                f.write(image_bytes)

def generate_images(prompt):
    """Run the asyncio event loop to generate images and then open them."""
    asyncio.run(generate_image(prompt))
    open_images(prompt)

def main():
    """Main loop to check for image generation requests."""
    while True:
        try:
            print(f"Attempting to open file: {STATUS_FILE}")  # Verify the file path
            if os.path.exists(STATUS_FILE):
                with open(STATUS_FILE, "r") as f:
                    data = f.read().strip()

                # Read prompt and status
                if ',' in data:
                    prompt, status = data.split(",")
                    prompt = prompt.strip()
                    status = status.strip()

                    if status == "True":
                        print("Generating Images")
                        generate_images(prompt=prompt)

                        # Update the status file to indicate completion
                        with open(STATUS_FILE, "w") as f:
                            f.write("False, False")
                        break
                    else:
                        sleep(1)
                else:
                    print("Error: Malformed data in the file. Ensure it's in the 'prompt,True' format.")
                    sleep(5)
            else:
                print(f"File not found: {STATUS_FILE}")
                sleep(5)

        except FileNotFoundError:
            print(f"Status file not found: {STATUS_FILE}")
            sleep(5)
        except Exception as e:
            print(f"Unexpected error: {e}")
            sleep(5)

if __name__ == "__main__":
    main()
