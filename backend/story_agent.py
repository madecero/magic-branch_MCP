# story_agent.py
import os
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda

load_dotenv()
llm = ChatOpenAI(model="gpt-4", temperature=0.8, api_key=os.getenv("OPENAI_API_KEY"))

async def generate_enticer(payload):
    """Generate a quick 2-3 sentence enticer to hook the user"""
    print("[story_agent] Generating enticer...")
    
    name = payload.get("name", "the child")
    age = payload.get("age", 4)
    gender = payload.get("gender", "neutral")
    interests = payload.get("interests", ["adventure"])
    
    interests_str = ", ".join(interests)
    
    enticer_prompt = (
        f"Create an exciting 2-3 sentence teaser for a children's story about a {age}-year-old {gender} named {name} who loves {interests_str}. "
        f"Make it magical and adventurous! End with something like 'What amazing adventures await? Stay tuned to find out!' "
        f"Keep it short, exciting, and age-appropriate."
    )
    
    result = llm.invoke([
        {"role": "system", "content": "You are a master storyteller who creates exciting teasers that make children eager to hear more."},
        {"role": "user", "content": enticer_prompt}
    ])
    
    enticer = result.content.strip()
    print(f"[story_agent] Generated enticer: {enticer}")
    return enticer

def generate_story(state):
    print("[story_agent] Received state:", state)

    name = state.get("name", "the child")
    age = state.get("age", 4)
    gender = state.get("gender", "neutral")
    interests = state.get("interests", ["adventure"])
    length = state.get("length", 5)

    interests_str = ", ".join(interests)
    
    system_prompt = (
        "You are a world-class children's storyteller who creates magical, age-appropriate stories. "
        "Each story should be imaginative, positive, and engaging for young readers."
    )
    
    user_prompt = (
        f"Write a story for a {age}-year-old {gender} named {name} who enjoys {interests}. "
        f"IMPORTANT: {name} is a {gender}. Make sure this is clear throughout.\n"
        f"First, provide a short, magical title on its own line.\n"
        f"Then, provide a 2-sentence summary that captures the magic and adventure of the story.\n"
        f"Then, the story with exactly {length} vivid, sequential paragraphs.\n\n"
        "After the story, separated by ---, provide detailed visual descriptions for the main character and any unique creatures mentioned (without naming them beyond generic terms like 'the unicorn'), in the format:\n"
        "Character descriptions:\n"
        f"- Main Character {name}: {name} is a {gender}. Highly detailed visual description to ensure consistency across illustrations: specify exact hair color and style, eye color, skin tone, facial features, typical clothing (that remains the same throughout), build, and any distinctive traits. Make it consistent and suitable for a children's book illustration.\n"
        "- [Generic Creature]: Highly detailed visual description to ensure consistency (only if creatures appear), including exact colors, textures, features, and accessories.\n"
        "Finally, after another ---, provide:\n"
        "Art style: A brief description of the illustration style (e.g., whimsical watercolor with vibrant colors and soft edges).\n"
        "Do not include these details in the story text itself."
    )

    result = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ])
    
    content = result.content.strip()
    
    # Parse the result
    lines = content.split('\n')
    title = lines[0].strip() if lines else f"{name}'s Adventure"
    
    # Find summary (should be after title)
    summary = ""
    story_start_idx = 1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() and not line.startswith('---'):
            # Look for 2-sentence summary pattern
            if len(line.split('.')) >= 2 and len(line) < 300:
                summary = line.strip()
                story_start_idx = i + 1
                break
    
    # Split into sections
    full_text = '\n'.join(lines[story_start_idx:])
    sections = full_text.split('---')
    
    story_text = sections[0].strip()
    story_pages = [p.strip() for p in story_text.split('\n') if p.strip()]
    
    # Parse character descriptions
    character_descriptions = {}
    if len(sections) > 1:
        char_section = sections[1].strip()
        for line in char_section.split('\n'):
            if line.strip().startswith('- '):
                parts = line.strip()[2:].split(':', 1)
                if len(parts) == 2:
                    char_name = parts[0].strip()
                    char_desc = parts[1].strip()
                    character_descriptions[char_name] = char_desc

    # Parse art style
    art_style = "whimsical, colorful children's book style"
    if len(sections) > 2:
        art_section = sections[2].strip()
        if art_section.startswith("Art style:"):
            art_style = art_section.replace("Art style:", "").strip()

    context = {
        "name": name,
        "age": age,
        "gender": gender,
        "interests": interests_str
    }

    state.update({
        "title": title,
        "summary": summary,
        "story_pages": story_pages,
        "character_descriptions": character_descriptions,
        "art_style": art_style,
        "context": context
    })

    print("[story_agent] Returning updated state:", state)
    return state

story_agent = RunnableLambda(generate_story)