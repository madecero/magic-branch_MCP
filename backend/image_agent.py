# image_agent.py (Updated)
import os
import openai
import requests
import tempfile
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def download_and_save_image(url):
    """Download an image and save it to a temp file, returning the file path."""
    response = requests.get(url)
    response.raise_for_status()
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    temp.write(response.content)
    temp.close()
    return temp.name

def generate_cover_image(story_data):
    """Generate just the book cover image"""
    print("[image_agent] Generating cover image")
    
    story_pages = story_data.get("story_pages", [])
    character_descriptions = story_data.get("character_descriptions", {})
    art_style = story_data.get("art_style", "whimsical, colorful children's book style")
    context = story_data.get("context", {})
    
    # ✅ BUILD COMPREHENSIVE CHARACTER DESCRIPTION (same as pages):
    char_desc_parts = []
    
    # Add main character info from context - BE EXPLICIT ABOUT GENDER
    if context.get("name"):
        gender = context.get("gender", "neutral")
        gender_desc = ""
        if gender == "girl":
            gender_desc = "girl"
        elif gender == "boy":
            gender_desc = "boy"
        elif gender == "neutral":
            gender_desc = "child"
        
        char_desc_parts.append(f"Main character: {context.get('name')} is a {gender_desc}, age {context.get('age', 4)}")
    
    # Add detailed character descriptions from story agent
    for name, desc in character_descriptions.items():
        char_desc_parts.append(f"{name}: {desc}")
    
    char_desc_str = ". ".join(char_desc_parts) if char_desc_parts else ""
    if char_desc_str:
        char_desc_str = f"Character details: {char_desc_str}."

    print(f"[image_agent] Character descriptions for cover: {char_desc_str}")

    # Summarize story for cover to shorten prompt
    full_story_summary = " ".join(story_pages)[:800] + "..." if len(" ".join(story_pages)) > 800 else " ".join(story_pages)

    # Generate book cover
    cover_prompt = (
        f"{art_style} book cover illustration without any text. {char_desc_str} "
        f"Story summary: {full_story_summary} "
        "Depict all main characters together in a scene that captures the essence of the story. "
        "Absolutely no text, letters, words, captions, titles, or any written elements in the image whatsoever; pure illustration only."
    )
    
    print(f"[image_agent] Cover prompt: {cover_prompt}")
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
        return cover_url
    except Exception as e:
        print(f"[image_agent] DALL·E API error for book cover: {e}")
        return "https://dummyimage.com/600x400/ff0000/fff&text=Error+Cover"
    
def generate_page_image(text, cover_image, page_index, character_descriptions=None, art_style=None, context=None):
    """Generate a single page image using the cover as reference"""
    print(f"[image_agent] Generating page {page_index + 1} image")
    
    if character_descriptions is None:
        character_descriptions = {}
    if art_style is None:
        art_style = "whimsical, colorful children's book style"
    if context is None:
        context = {}
    
    # ✅ BUILD COMPREHENSIVE CHARACTER DESCRIPTION:
    char_desc_parts = []
    
    # Add main character info from context - BE EXPLICIT ABOUT GENDER
    if context.get("name"):
        gender = context.get("gender", "neutral")
        gender_desc = ""
        if gender == "girl":
            gender_desc = "girl"
        elif gender == "boy":
            gender_desc = "boy"
        elif gender == "neutral":
            gender_desc = "child"
        
        char_desc_parts.append(f"Main character: {context.get('name')} is a {gender_desc}, age {context.get('age', 4)}")
    
    # Add detailed character descriptions from story agent
    for name, desc in character_descriptions.items():
        char_desc_parts.append(f"{name}: {desc}")
    
    char_desc_str = ". ".join(char_desc_parts) if char_desc_parts else ""
    if char_desc_str:
        char_desc_str = f"Character details: {char_desc_str}."

    print(f"[image_agent] Character descriptions for page {page_index + 1}: {char_desc_str}")

    prompt = (
        f"{art_style} page illustration without any text. {char_desc_str} "
        f"Illustrate this scene: {text} "
        "Keep ALL characters visually identical to their detailed descriptions and the book cover - same hair, eyes, clothes, gender presentation, everything. "
        "Absolutely no text, letters, words, captions, signs, or any written elements in the image whatsoever; pure illustration only."
    )
    
    print(f"[image_agent] Page {page_index + 1} prompt: {prompt}")
    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="standard"
        )
        image_url = response.data[0].url
        print(f"[image_agent] Got page {page_index + 1} image URL: {image_url}")
        return image_url
    except Exception as e:
        print(f"[image_agent] DALL·E API error for page {page_index + 1}: {e}")
        return f"https://dummyimage.com/600x400/ff0000/fff&text=Error+Page+{page_index + 1}"
       
# Keep the original function for backward compatibility
def generate_images(state):
    print("[image_agent] Received state:", state)

    story_chunks = state.get("story_pages")
    if not story_chunks:
        raise ValueError("Missing story_pages in state.")

    character_descriptions = state.get("character_descriptions", {})
    art_style = state.get("art_style", "whimsical, colorful children's book style")

    # Generate cover
    cover_url = generate_cover_image({
        "story_pages": story_chunks,
        "character_descriptions": character_descriptions,
        "art_style": art_style
    })

    # Generate page images
    image_pages = []
    for i, chunk in enumerate(story_chunks):
        image_url = generate_page_image(
            text=chunk,
            cover_image=cover_url,
            page_index=i,
            character_descriptions=character_descriptions,
            art_style=art_style
        )
        
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