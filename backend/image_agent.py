# image_agent.py (Updated)
import os
import openai
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def generate_images(state):
    print("[image_agent] Received state:", state)

    story_chunks = state.get("story_pages")
    if not story_chunks:
        raise ValueError("Missing story_pages in state.")

    character_descriptions = state.get("character_descriptions", {})
    # Clean join without extra periods
    char_desc_str = " ".join([f"{name}: {desc}." for name, desc in character_descriptions.items()]) if character_descriptions else ""
    if char_desc_str:
        char_desc_str = f"Characters: {char_desc_str}"

    art_style = state.get("art_style", "whimsical, colorful children's book style")

    # Summarize story for cover to shorten prompt
    full_story_summary = " ".join(story_chunks)[:1000] + "..." if len(" ".join(story_chunks)) > 1000 else " ".join(story_chunks)

    # Generate book cover
    cover_prompt = (
        f"{art_style} book cover illustration without any text. {char_desc_str} "
        f"Story summary: {full_story_summary} "
        "Depict all main characters together in a scene that captures the essence of the story. "
        "Absolutely no text, letters, words, captions, titles, or any written elements in the image whatsoever; pure illustration only."
    )
    print(f"[image_agent] Generating book cover with DALL·E: {cover_prompt}")
    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=cover_prompt,
            n=1,
            size="1024x1024",
            quality="standard"
        )
        cover_url = response.data[0].url
        print(f"[image_agent] Got DALL·E book cover URL: {cover_url}")
    except Exception as e:
        print(f"[image_agent] DALL·E API error for book cover: {e}")
        cover_url = "https://dummyimage.com/600x400/ff0000/fff&text=Error+Cover"

    image_pages = []
    for i, chunk in enumerate(story_chunks):
        prompt = (
            f"{art_style} page illustration without any text. {char_desc_str} "
            f"Illustrate this scene: {chunk} "
            "Keep the characters visually consistent with their descriptions. "
            "Absolutely no text, letters, words, captions, signs, or any written elements in the image whatsoever; pure illustration only."
        )
        print(f"[image_agent] Generating page {i+1} with DALL·E. Prompt: {prompt}")
        try:
            response = openai.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size="1024x1024",
                quality="standard"
            )
            image_url = response.data[0].url
            print(f"[image_agent] Got page {i+1} image URL: {image_url}")
        except Exception as e:
            print(f"[image_agent] DALL·E API error for page {i+1}: {e}")
            image_url = f"https://dummyimage.com/600x400/ff0000/fff&text=Error+Page+{i+1}"

        if not isinstance(image_url, str) or not image_url.startswith("http"):
            image_url = "https://dummyimage.com/600x400/ff0000/fff&text=Error"

        image_pages.append({
            "text": chunk,
            "image": image_url
        })

    state["cover_image"] = cover_url
    state["image_pages"] = image_pages
    print("[image_agent] Returning updated state:", state)
    return state