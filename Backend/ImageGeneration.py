import asyncio
from random import randint
from PIL import Image
import os
from time import sleep

from diffusers import StableDiffusionPipeline
import torch

# ✅ Create Data folder if not exists
if not os.path.exists("Data"):
    os.makedirs("Data")

# ✅ Load model once with lower inference steps
print("🧠 Loading Stable Diffusion model locally...")
pipe = StableDiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-2-1",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
)
pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")
pipe.scheduler.set_timesteps(25)  # 🔁 Reduced for faster generation

# ✅ Generate images (sequentially)
async def generate_image(prompt: str):
    for i in range(4):
        full_prompt = f"{prompt}, high quality, detailed, seed={randint(0, 1000000)}"
        result = await asyncio.to_thread(pipe, full_prompt)
        image = result.images[0]
        filename = fr"Data\{prompt.replace(' ', '_')}{i + 1}.jpg"
        image.save(filename)
        print(f"✅ Saved: {filename}")

# ✅ Open images
def open_images(prompt):
    folder_path = r"Data"
    prompt = prompt.replace(" ", "_")
    files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in files:
        image_path = os.path.join(folder_path, jpg_file)
        if os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                print(f"✅ Opened image: {image_path}")
                img.show()
                sleep(1)
            except IOError:
                print(f"❌ Unable to open {image_path}")
        else:
            print(f"❌ File not found: {image_path}")

# ✅ Combine generate + open
def GenerateImages(prompt: str):
    asyncio.run(generate_image(prompt))
    open_images(prompt)

# ✅ Main loop to check .data file
while True:
    try:
        with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
            data = f.read()

        prompt, status = data.split(",")

        if status.strip().lower() == "true":
            print("🖼 Generating Images...")
            GenerateImages(prompt.strip())

            with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                f.write("False,False")
            break
        else:
            sleep(1)

    except Exception as e:
        print(f"⚠ Error: {e}")
        sleep(1)
