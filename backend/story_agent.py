# story_agent.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda

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
    
    # ✅ MAKE THE PROMPT MORE EXPLICIT
    user_prompt = (
        f"Write a story for a {age}-year-old {gender} named {name} who enjoys {interests_str}. "
        f"IMPORTANT: {name} is a {gender}. Make sure this is clear throughout.\n\n"
        
        f"FORMAT YOUR RESPONSE EXACTLY LIKE THIS:\n"
        f"TITLE: [Short magical title]\n"
        f"SUMMARY: [2-sentence summary of the adventure]\n"
        f"STORY:\n"
        f"[Paragraph 1 of {length}]\n"
        f"[Paragraph 2 of {length}]\n"
        f"[Continue for exactly {length} paragraphs]\n"
        f"---\n"
        f"CHARACTER DESCRIPTIONS:\n"
        f"- Main Character {name}: {name} is a {gender}. [Detailed visual description]\n"
        f"- [Any other characters]: [Detailed descriptions]\n"
        f"---\n"
        f"ART STYLE: [Description of illustration style]\n\n"
        
        f"Make sure to include exactly {length} story paragraphs between STORY: and the first ---"
    )

    result = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ])
    
    content = result.content.strip()
    print(f"[story_agent] Raw LLM response: {content}")  # ✅ DEBUG LOG
    
    # ✅ MORE ROBUST PARSING
    lines = content.split('\n')
    title = f"{name}'s Adventure"
    summary = f"{name} discovers something magical and wonderful in this enchanting tale."
    story_pages = []
    character_descriptions = {}
    art_style = "detailed, magical illustration in the style of Harry Potter book illustrations, with rich colors, intricate details, and a sense of mystery"
    
    try:
        # Find title
        for line in lines:
            if line.strip().upper().startswith('TITLE:'):
                title = line.strip()[6:].strip()
                break
        
        # Find summary
        for line in lines:
            if line.strip().upper().startswith('SUMMARY:'):
                summary = line.strip()[8:].strip()
                break
        
        # Find story section
        story_start = -1
        story_end = -1
        for i, line in enumerate(lines):
            if line.strip().upper().startswith('STORY:'):
                story_start = i + 1
            elif story_start != -1 and line.strip() == '---':
                story_end = i
                break
        
        if story_start != -1:
            if story_end == -1:
                story_end = len(lines)
            
            # Extract story paragraphs
            story_lines = lines[story_start:story_end]
            story_pages = [line.strip() for line in story_lines if line.strip()]
            
            # Ensure we have the right number of pages
            if len(story_pages) != length:
                print(f"[story_agent] Warning: Expected {length} pages, got {len(story_pages)}")
        
        # Find character descriptions
        char_start = -1
        char_end = -1
        for i, line in enumerate(lines):
            if 'CHARACTER DESCRIPTIONS:' in line.upper():
                char_start = i + 1
            elif char_start != -1 and line.strip() == '---':
                char_end = i
                break
        
        if char_start != -1:
            if char_end == -1:
                char_end = len(lines)
            
            for line in lines[char_start:char_end]:
                if line.strip().startswith('- '):
                    parts = line.strip()[2:].split(':', 1)
                    if len(parts) == 2:
                        char_name = parts[0].strip()
                        char_desc = parts[1].strip()
                        character_descriptions[char_name] = char_desc
        
        # Find art style
        for line in lines:
            if line.strip().upper().startswith('ART STYLE:'):
                art_style = line.strip()[10:].strip()
                break
    
    except Exception as e:
        print(f"[story_agent] Parsing error: {e}")
    
    # ✅ FALLBACK: If story_pages is empty, create a simple story
    if not story_pages:
        print("[story_agent] No story pages found, creating fallback story")
        story_pages = [
            f"{name} discovered a magical world filled with {interests_str}.",
            f"With courage and wonder, {name} explored this enchanting place.",
            f"{name} met friendly creatures who became great companions.",
            f"Together, they went on amazing adventures full of joy and discovery.",
            f"{name} returned home with a heart full of magical memories."
        ][:length]  # Trim to requested length
    
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