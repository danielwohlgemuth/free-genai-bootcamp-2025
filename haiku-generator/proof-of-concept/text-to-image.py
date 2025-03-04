import torch
from diffusers import StableDiffusion3Pipeline
# from huggingface_hub import login
import os


# login()

HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN", None)

pipe = StableDiffusion3Pipeline.from_pretrained("stabilityai/stable-diffusion-3.5-medium", token=HUGGINGFACEHUB_API_TOKEN)

device = "cuda" if torch.cuda.is_available() else "cpu"
pipe = pipe.to(device)

image = pipe(
    """A large autumn tree with vibrant orange and yellow leaves, some leaves floating away.
A clear blue sky as a backdrop to ensure contrast.
Visible wind currents (soft, white streaks) to represent the breeze.
A single leaf in the foreground, slightly blurred, to show movement.
No unnecessary background elements that clutter the image.""",
    num_inference_steps=5, # ~60 seconds per step
    guidance_scale=4.5,
).images[0]
image.save("tree.png")
