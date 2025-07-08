import os
import replicate
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

load_dotenv()
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

def extract_url(output):
    """Extract a URL string from Replicate output (FileOutput, string, or list)."""
    if isinstance(output, list):
        first = output[0]
    else:
        first = output
    return getattr(first, "url", str(first))

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
            # 1. Generate first image with SDXL
            print(f"[image_agent] Generating SDXL Turbo image for page 1 with prompt: {prompt}")
            try:
                output = replicate.run(
                    "stability-ai/sdxl:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc",
                    input={
                        "prompt": prompt,
                        "width": 1024,
                        "height": 1024,
                        "num_inference_steps": 30,
                        "guidance_scale": 2.5,
                    }
                )
                image_url = extract_url(output)
                print(f"[image_agent] Got SDXL Turbo image URL for page 1: {image_url}")

                # 2. Generate canny edge map from the first image
                canny_input = {
                    "image": image_url,
                    "threshold_a": 100,
                    "threshold_b": 200,
                    "prompt": prompt
                }
                print(f"[image_agent] Canny model input: {canny_input}")
                canny_output = replicate.run(
                    "jagilley/controlnet-canny:aff48af9c68d162388d230a2ab003f68d2638d88307bdaf1c2f1ac95079c9613",
                    input=canny_input
                )
                print(f"[image_agent] Raw canny_output type: {type(canny_output)}, value: {canny_output}")
                canny_image_url = extract_url(canny_output)
                print(f"[image_agent] Got canny edge image URL: {canny_image_url}")

            except Exception as e:
                print(f"[image_agent] SDXL Turbo or canny edge API error for page 1: {e}")
                image_url = "https://dummyimage.com/600x400/ff0000/fff&text=Error+Page+1"
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
                image_url = extract_url(output)
                print(f"[image_agent] Got SDXL+ControlNet image URL for page {i+1}: {image_url}")
            except Exception as e:
                print(f"[image_agent] Replicate API error for page {i+1}: {e}")
                image_url = f"https://dummyimage.com/600x400/ff0000/fff&text=Error+Page+{i+1}"

        # Defensive: ensure image_url is always a string URL
        if not isinstance(image_url, str) or not image_url.startswith("http"):
            image_url = "https://dummyimage.com/600x400/ff0000/fff&text=Error"

        image_pages.append({
            "text": chunk,
            "image": image_url
        })

    state["image_pages"] = image_pages
    print("[image_agent] Returning updated state:", state)
    return state

generate_images = RunnableLambda(generate_images)