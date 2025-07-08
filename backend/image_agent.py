import os
import replicate
import requests
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

load_dotenv()
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

def generate_images(state):
    print("[image_agent] Received state:", state)

    story_chunks = state.get("story_pages")
    if not story_chunks:
        raise ValueError("Missing story_pages in state.")

    context = state.get("context", {})
    character_desc = (
        f"Main character: {context.get('name', '')}, "
        f"age {context.get('age', '')}, gender {context.get('gender', '')}, "
        f"interests: {context.get('interests', '')}."
    )

    image_pages = []
    canny_image_url = None

    for i, chunk in enumerate(story_chunks):
        prompt = (
            f"{character_desc} "
            f"Illustrate this scene: {chunk} "
            "Keep the main character(s) visually consistent with previous pages. "
            "Do not include any text, captions, or words in the image."
        )

        if i == 0:
            # 1. Generate first image with SDXL Turbo
            print(f"[image_agent] Generating SDXL Turbo image for page 1 with prompt: {prompt}")
            try:
                output = replicate.run(
                    "stability-ai/sdxl-turbo:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                    input={
                        "prompt": prompt,
                        "width": 1024,
                        "height": 1024,
                        "num_inference_steps": 30,
                        "guidance_scale": 2.5,
                    }
                )
                image_url = output[0] if isinstance(output, list) else output
                print(f"[image_agent] Got SDXL Turbo image URL for page 1: {image_url}")

                # 2. Generate canny edge map from the first image
                print(f"[image_agent] Generating canny edge map for page 1 image")
                canny_output = replicate.run(
                    "ai-forever/kandinsky-2.2-controlnet-canny:dbb8e7e2e9c2e7b7e7e8e7e8e7e8e7e8e7e8e7e8e7e8e7e8e7e8e7e8e7e8",
                    input={
                        "image": image_url,
                        "threshold_a": 100,
                        "threshold_b": 200
                    }
                )
                canny_image_url = canny_output[0] if isinstance(canny_output, list) else canny_output
                print(f"[image_agent] Got canny edge image URL: {canny_image_url}")

            except Exception as e:
                print(f"[image_agent] SDXL Turbo or canny edge API error for page 1: {e}")
                image_url = f"https://dummyimage.com/600x400/ff0000/fff&text=Error+Page+1"
                canny_image_url = None

        else:
            # 3. Use SDXL + ControlNet for subsequent images
            print(f"[image_agent] Generating SDXL+ControlNet image for page {i+1} with prompt: {prompt}")
            inputs = {
                "prompt": prompt,
                "num_inference_steps": 30,
                "width": 1024,
                "height": 1024,
                "guidance_scale": 7.5,
                "negative_prompt": "text, caption, subtitle, watermark, words, letters, writing",
                "image": canny_image_url,
                "conditioning_scale": 0.7
            }
            try:
                output = replicate.run(
                    "lucataco/sdxl-controlnet:06d6fae3b75ab68a28cd2900afa6033166910dd09fd9751047043a5bbb4c184b",
                    input=inputs
                )
                image_url = output[0] if isinstance(output, list) else output
                print(f"[image_agent] Got SDXL+ControlNet image URL for page {i+1}: {image_url}")
            except Exception as e:
                print(f"[image_agent] Replicate API error for page {i+1}: {e}")
                image_url = f"https://dummyimage.com/600x400/ff0000/fff&text=Error+Page+{i+1}"

        image_pages.append({
            "text": chunk,
            "image": image_url
        })

    state["image_pages"] = image_pages
    print("[image_agent] Returning updated state:", state)
    return state

generate_images = RunnableLambda(generate_images)