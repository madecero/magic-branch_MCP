# story_agent.py (Updated)
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda

load_dotenv()
llm = ChatOpenAI(model="gpt-4", temperature=0.8, api_key=os.getenv("OPENAI_API_KEY"))

def generate_story(state):
    print("[story_agent] Received state:", state)

    name = state.get("name", "the child")
    gender = state.get("gender", "neutral")
    age = state.get("age", 4)
    interests = ", ".join(state.get("interests", []))
    length = state.get("length", 5)

    system_prompt = (
        f"You are a storybook AI that creates vivid, connected stories for children. "
        f"The main character is a {age}-year-old {gender} named {name} who enjoys {interests}. "
        f"Generate exactly {length} paragraphs. Each paragraph is a coherent story page. "
        "Keep a magical, cohesive narrative arc across all pages. "
        "Focus the story on the main child character. Do not introduce any new named characters; keep any creatures or elements generic (e.g., 'a friendly unicorn' instead of naming it). "
        "You may include magical elements like those in the child's interests, but without giving them proper names."
    )

    user_prompt = (
        f"Write a story for a {age}-year-old named {name} who enjoys {interests}. "
        f"First, provide a short, magical title on its own line.\n"
        f"Then, the story with exactly {length} vivid, sequential paragraphs.\n\n"
        "After the story, separated by ---, provide detailed visual descriptions for the main character and any unique creatures mentioned (without naming them beyond generic terms like 'the unicorn'), in the format:\n"
        "Character descriptions:\n"
        "- Main Character {name}: Highly detailed visual description to ensure consistency across illustrations: specify exact hair color and style, eye color, skin tone, facial features, typical clothing (that remains the same throughout), build, and any distinctive traits. Make it consistent and suitable for a children's book illustration.\n"
        "- [Generic Creature]: Highly detailed visual description to ensure consistency (only if creatures appear), including exact colors, textures, features, and accessories.\n"
        "Finally, after another ---, provide:\n"
        "Art style: A brief description of the illustration style (e.g., whimsical watercolor with vibrant colors and soft edges).\n"
        "Do not include these details in the story text itself."
    )

    result = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ])

    print("[story_agent] LLM Result:", result.content)

    # Parse the output
    parts = result.content.split("---")
    if len(parts) >= 3:
        # Title is first line
        title = parts[0].strip().split("\n")[0].strip()
        # Story is the rest of part 0 after title + paragraphs
        story_text = "\n".join(parts[0].strip().split("\n")[1:]) + "\n\n" + parts[1].strip() if len(parts) > 1 else parts[0].strip()
        pages = [p.strip() for p in story_text.split("\n\n") if p.strip()]
        
        # Character descriptions from second part
        desc_part = parts[1].strip() if len(parts) > 1 else ""
        desc_lines = [line.strip() for line in desc_part.split("\n") if line.strip() and line.startswith("- ")]
        character_descriptions = {}
        for line in desc_lines:
            try:
                char_name, desc = line[2:].split(":", 1)
                # Strip trailing punctuation for cleaner join later
                desc = desc.strip().rstrip('.')
                character_descriptions[char_name.strip()] = desc
            except ValueError:
                continue
        
        # Art style from third part
        art_part = parts[2].strip() if len(parts) > 2 else ""
        art_style = art_part.replace("Art style:", "").strip() if art_part.startswith("Art style:") else "whimsical, colorful children's book style"
    else:
        title = "A Magical Adventure"
        pages = [p.strip() for p in result.content.split("\n\n") if p.strip()]
        character_descriptions = {}
        art_style = "whimsical, colorful children's book style"

    if not pages:
        raise ValueError("No story content returned from model.")

    state["title"] = title
    state["story_pages"] = pages[:length]
    state["context"] = {
        "name": name,  # Ensure this is the child's name (debug if overriding)
        "age": age,
        "gender": gender,
        "interests": interests
    }
    state["character_descriptions"] = character_descriptions
    state["art_style"] = art_style

    print("[story_agent] Returning updated state:", state)
    return state

story_agent = RunnableLambda(generate_story)