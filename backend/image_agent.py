# image_agent.py 
import os
import json
import openai
import requests
import tempfile
from dotenv import load_dotenv
import asyncio

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Add LLM for generating structured prompts (using ChatOpenAI for consistency with story_agent)
from langchain_openai import ChatOpenAI # pyright: ignore[reportMissingImports]
llm = ChatOpenAI(model="gpt-4", temperature=0.2, api_key=OPENAI_API_KEY)  # Lower temp for precise prompts

def download_and_save_image(url):
    """Download an image and save it to a temp file, returning the file path."""
    response = requests.get(url)
    response.raise_for_status()
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    temp.write(response.content)
    temp.close()
    return temp.name

def generate_dalle_prompt(system_prompt, user_prompt):
    """Helper to generate DALL-E prompt via LLM in JSON format."""
    result = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ])
    
    content = result.content.strip()
    print(f"[image_agent] Raw LLM prompt response: {content}")  # Log raw for debugging
    
    try:
        parsed = json.loads(content)
        dalle_prompt = parsed.get("prompt", "")
        # Log key elements for visibility
        print(f"[image_agent] Parsed DALL-E prompt: {dalle_prompt}")
        if "reasoning" in parsed:
            print(f"[image_agent] Prompt reasoning: {parsed.get('reasoning')}")
        
        if not dalle_prompt:
            raise ValueError("No 'prompt' key in JSON")
        
        return dalle_prompt
    except (json.JSONDecodeError, ValueError) as e:
        print(f"[image_agent] JSON parsing error in prompt generation: {e}. Falling back to default.")
        return "A magical children's book illustration in portrait mode."  # Simple fallback

def generate_cover_image(story_data):
    """Generate just the book cover image using JSON-structured prompt."""
    print("[image_agent] Generating cover image")
    
    story_pages = story_data.get("story_pages", [])
    character_descriptions = story_data.get("character_descriptions", {})
    art_style = story_data.get("art_style", "detailed, magical illustration in the style of Harry Potter book covers, with rich colors, intricate details, and a sense of mystery")
    context = story_data.get("context", {})
    
    # BUILD COMPREHENSIVE CHARACTER DESCRIPTION
    char_desc_parts = []
    
    if context.get("name"):
        gender = context.get("gender", "neutral")
        gender_desc = "child" if gender == "neutral" else gender
        char_desc_parts.append(f"Main character: {context.get('name')} is a {gender_desc}, age {context.get('age', 4)}")
    
    for name, desc in character_descriptions.items():
        char_desc_parts.append(f"{name}: {desc}")
    
    char_desc_str = ". ".join(char_desc_parts) if char_desc_parts else ""
    if char_desc_str:
        char_desc_str = f"Character details: {char_desc_str}."

    print(f"[image_agent] Character descriptions for cover: {char_desc_str}")

    full_story_summary = " ".join(story_pages)[:800] + "..." if len(" ".join(story_pages)) > 800 else " ".join(story_pages)

    # System prompt for LLM to generate DALL-E prompt in JSON
    system_prompt = (
        "You are an expert DALL-E prompt engineer for children's book covers. "
        "Create highly detailed, consistent prompts that ensure visual continuity. "
        "Output ONLY valid JSON (no extra text) with these keys: "
        "'prompt': the full DALL-E prompt string, "
        "'reasoning': a short explanation of why this prompt ensures consistency and quality."
    )
    
    user_prompt = (
        f"Generate a DALL-E prompt for a book cover based on: "
        f"Art style: {art_style}. "
        f"{char_desc_str} "
        f"Story summary: {full_story_summary}. "
        "Depict all main characters together in a scene that captures the essence of the story. "
        "Use a vertical, portrait-oriented composition to emphasize height and depth, suitable for a book cover. "
        "Compose the illustration to fill the frame but leave the bottom third as a subtle, non-distracting background area suitable for text overlay, with no important elements or characters in that space. "
        "ABSOLUTELY NO TEXT ALLOWED: Strictly no text, letters, words, captions, titles, signs, labels, or any written elements anywhere in the image; pure illustration only. "
        "Do not include any form of text under any circumstances—this is critical and must be followed exactly. The image must be 100% text-free. "
        "Ensure the prompt is optimized for DALL-E-3, vivid, and engaging for children."
    )
    
    dalle_prompt = generate_dalle_prompt(system_prompt, user_prompt)
    print(f"[image_agent] Final cover prompt: {dalle_prompt}")
    
    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=dalle_prompt,
            n=1,
            size="1024x1792",  # Locked to portrait
            quality="standard"
        )
        cover_url = response.data[0].url
        print(f"[image_agent] Got DALL·E book cover URL: {cover_url}")
        return cover_url
    except Exception as e:
        print(f"[image_agent] DALL·E API error for book cover: {e}")
        return "https://dummyimage.com/600x400/ff0000/fff&text=Error+Cover"

def generate_page_image(text, cover_image, page_index, character_descriptions=None, art_style=None, context=None):
    """Generate a single page image using the cover as reference, with JSON-structured prompt."""
    print(f"[image_agent] Generating page {page_index + 1} image")
    
    if character_descriptions is None:
        character_descriptions = {}
    if art_style is None:
        art_style = "detailed, magical illustration in the style of Harry Potter book illustrations, with rich colors, intricate details, and a sense of mystery"
    if context is None:
        context = {}
    
    char_desc_parts = []
    
    if context.get("name"):
        gender = context.get("gender", "neutral")
        gender_desc = "child" if gender == "neutral" else gender
        char_desc_parts.append(f"Main character: {context.get('name')} is a {gender_desc}, age {context.get('age', 4)}")
    
    for name, desc in character_descriptions.items():
        char_desc_parts.append(f"{name}: {desc}")
    
    char_desc_str = ". ".join(char_desc_parts) if char_desc_parts else ""
    if char_desc_str:
        char_desc_str = f"Character details: {char_desc_str}."

    print(f"[image_agent] Character descriptions for page {page_index + 1}: {char_desc_str}")

    # System prompt for LLM to generate DALL-E prompt in JSON
    system_prompt = (
        "You are an expert DALL-E prompt engineer for children's book page illustrations. "
        "Create highly detailed, consistent prompts that match the book cover and ensure visual continuity across pages. "
        "Output ONLY valid JSON (no extra text) with these keys: "
        "'prompt': the full DALL-E prompt string, "
        "'reasoning': a short explanation of why this prompt ensures consistency and quality."
    )
    
    user_prompt = (
        f"Generate a DALL-E prompt for a story page illustration based on: "
        f"Art style: {art_style}. "
        f"{char_desc_str} "
        f"Scene to illustrate: {text}. "
        "Keep ALL characters visually identical to their detailed descriptions and the book cover - same hair, eyes, clothes, gender presentation, everything. "
        "Use a vertical, portrait-oriented composition to emphasize height and depth, filling the tall frame naturally. "
        "Compose the illustration to fill the frame but leave the bottom third as a subtle, non-distracting background area suitable for text overlay, with no important elements or characters in that space. "
        "ABSOLUTELY NO TEXT ALLOWED: Strictly no text, letters, words, captions, signs, labels, or any written elements anywhere in the image; pure illustration only. "
        "Do not include any form of text under any circumstances—this is critical and must be followed exactly. The image must be 100% text-free. "
        "Ensure the prompt is optimized for DALL-E-3, vivid, and engaging for children."
    )
    
    dalle_prompt = generate_dalle_prompt(system_prompt, user_prompt)
    print(f"[image_agent] Final page {page_index + 1} prompt: {dalle_prompt}")
    
    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=dalle_prompt,
            n=1,
            size="1024x1792",  # Locked to portrait
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
    art_style = state.get("art_style", "detailed, magical illustration in the style of Harry Potter book illustrations, with rich colors, intricate details, and a sense of mystery")
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