# story_agent.py
import os
import json  # Add this for parsing
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI # pyright: ignore[reportMissingImports]
from langchain_core.runnables import RunnableLambda # pyright: ignore[reportMissingImports]

load_dotenv()
llm = ChatOpenAI(model="gpt-4", temperature=0.8, api_key=os.getenv("OPENAI_API_KEY"))

def generate_story(state):
    print("[story_agent] Received state:", state)

    name = state.get("name", "the child")
    age = state.get("age", 4)
    gender = state.get("gender", "neutral")
    interests = state.get("interests", ["adventure"])
    length = state.get("length", 5)

    interests_str = ", ".join(interests)
    
    system_prompt = (
        "You are a world-class children's storyteller inspired by 'The Alchemist', creating subtle, mystical stories with themes of destiny, self-discovery, and hidden wonders. "
        "Magic is understated—more like synchronicities, inner wisdom, and natural mysteries than spells or wands. Stories are imaginative, positive, and engaging for young readers."
    )
    
    # Updated prompt: Instruct for JSON output only, keeping your original content
    user_prompt = (
        f"Write a story for a {age}-year-old {gender} named {name} who enjoys {interests_str}. "
        f"IMPORTANT: {name} is a {gender}. Make sure this is clear throughout.\n\n"
        
        "Output ONLY valid JSON (no extra text, explanations, or markdown). Use this exact structure:\n"
        "{\n"
        '  "title": "[Short magical title]",\n'
        '  "summary": "[2-sentence summary of the adventure]",\n'
        '  "story_pages": ["[Paragraph 1]", "[Paragraph 2]", ...],  // Exactly ' + str(length) + ' paragraphs as an array\n'
        '  "character_descriptions": {\n'
        '    "Main Character ' + name + '": "' + name + ' is a ' + gender + '. [Detailed visual description]",\n'
        '    "[Any other character name]": "[Detailed visual description]",\n'
        '    // Add entries for all key characters\n'
        '  },\n'
        '  "art_style": "[Description of illustration style]"\n'
        "}\n\n"
        
        f"Ensure exactly {length} story paragraphs in the array."
    )

    result = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ])
    
    content = result.content.strip()
    print(f"[story_agent] Raw LLM response: {content}")  # Log raw for debugging
    
    # Parse JSON (much simpler and robust now)
    try:
        parsed = json.loads(content)
        title = parsed.get("title", f"{name}'s Adventure")
        summary = parsed.get("summary", f"{name} discovers something magical and wonderful in this enchanting tale.")
        story_pages = parsed.get("story_pages", [])
        character_descriptions = parsed.get("character_descriptions", {})
        art_style = parsed.get("art_style", "detailed, magical illustration in the style of Harry Potter book illustrations, with rich colors, intricate details, and a sense of mystery")
        
        # Log key elements for visibility (as you requested)
        print(f"[story_agent] Parsed title: {title}")
        print(f"[story_agent] Parsed summary: {summary}")
        print(f"[story_agent] Parsed story_pages (count: {len(story_pages)}): {story_pages}")
        print(f"[story_agent] Parsed character_descriptions: {character_descriptions}")
        print(f"[story_agent] Parsed art_style: {art_style}")
        
        # Validate length
        if len(story_pages) != length:
            print(f"[story_agent] Warning: Expected {length} pages, got {len(story_pages)}")

    except json.JSONDecodeError as e:
        print(f"[story_agent] JSON parsing error: {e}. Falling back to defaults.")
        title = f"{name}'s Adventure"
        summary = f"{name} discovers something magical and wonderful in this enchanting tale."
        story_pages = []
        character_descriptions = {}
        art_style = "detailed, magical illustration in the style of Harry Potter book illustrations, with rich colors, intricate details, and a sense of mystery"
    
    # Fallback: If story_pages is empty, create a simple story (now as list for JSON consistency)
    if not story_pages:
        print("[story_agent] No story pages found, creating fallback story")
        story_pages = [
            f"{name} discovered a magical world filled with {interests_str}.",
            f"With courage and wonder, {name} explored this enchanting place.",
            f"{name} met friendly creatures who became great companions.",
            f"Together, they went on amazing adventures full of joy and discovery.",
            f"{name} returned home with a heart full of magical memories."
        ][:length]
    
    context = {
        "name": name,
        "age": age,
        "gender": gender,
        "interests": interests_str
    }

    final_state = {
        "title": title,
        "summary": summary,
        "story_pages": story_pages,
        "character_descriptions": character_descriptions,
        "art_style": art_style,
        "context": context
    }
    
    state.update(final_state)
    
    print(f"[story_agent] Final parsed state: title='{title}', summary='{summary}', pages={len(story_pages)}, chars={len(character_descriptions)}")
    return state

story_agent = RunnableLambda(generate_story)