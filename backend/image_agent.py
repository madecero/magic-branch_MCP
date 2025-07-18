# image_agent.py (Updated)
import os
import openai
import requests
import tempfile
from dotenv import load_dotenv
import asyncio

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

    # Generate book cover with space for text
    cover_prompt = (
        f"{art_style} book cover illustration without any text. {char_desc_str} "
        f"Story summary: {full_story_summary} "
        "Depict all main characters together in a scene that captures the essence of the story. "
        "Compose the illustration to fill the frame but leave the bottom third as a subtle, non-distracting background area (e.g., soft gradient or simple pattern) suitable for text overlay, with no important elements or characters in that space. "
        "Absolutely no text, letters, words, captions, titles, or any written elements in the image whatsoever; pure illustration only."
    )
    
    print(f"[image_agent] Cover prompt: {cover_prompt}")
    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=cover_prompt,
            n=1,
            size="1024x1792",  # Taller aspect for full-screen feel with text space
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
        "Compose the illustration to fill the frame but leave the bottom third as a subtle, non-distracting background area (e.g., soft gradient or simple pattern) suitable for text overlay, with no important elements or characters in that space. "
        "Absolutely no text, letters, words, captions, signs, or any written elements in the image whatsoever; pure illustration only."
    )
    
    print(f"[image_agent] Page {page_index + 1} prompt: {prompt}")
    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1792",  # Taller for mobile full-screen with text space
            quality="standard"
        )
        image_url = response.data[0].url
        print(f"[image_agent] Got page {page_index + 1} image URL: {image_url}")
        return image_url
    except Exception as e:
        print(f"[image_agent] DALL·E API error for page {page_index + 1}: {e}")
        return f"https://dummyimage.com/600x400/ff0000/fff&text=Error+Page+{page_index + 1}"

async def generate_page_image_async(text, cover_image, page_index, character_descriptions=None, art_style=None, context=None):
    """Async wrapper for generate_page_image"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, generate_page_image, text, cover_image, page_index, character_descriptions, art_style, context)

async def generate_images(state):
    print("[image_agent] Received state:", state)

    story_chunks = state.get("story_pages")
    if not story_chunks:
        raise ValueError("Missing story_pages in state.")

    character_descriptions = state.get("character_descriptions", {})
    art_style = state.get("art_style", "whimsical, colorful children's book style")
    context = state.get("context", {})

    # Generate cover (sync for now, as it's single)
    cover_url = generate_cover_image({
        "story_pages": story_chunks,
        "character_descriptions": character_descriptions,
        "art_style": art_style,
        "context": context
    })

    # Generate page images in parallel
    tasks = []
    for i, chunk in enumerate(story_chunks):
        tasks.append(generate_page_image_async(
            chunk, cover_url, i, character_descriptions, art_style, context
        ))
    
    image_urls = await asyncio.gather(*tasks, return_exceptions=True)
    
    image_pages = []
    for i, url_or_exc in enumerate(image_urls):
        if isinstance(url_or_exc, Exception):
            url = "https://dummyimage.com/1024x1024/eee&text=Loading..."  # Placeholder for errors
        else:
            url = url_or_exc if isinstance(url_or_exc, str) else "https://dummyimage.com/1024x1024/eee&text=Loading..."
        image_pages.append({"text": story_chunks[i], "image": url})

    state["cover_image"] = cover_url
    state["image_pages"] = image_pages
    print("[image_agent] Returning updated state:", state)
    return state