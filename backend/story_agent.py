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
        "Keep a magical, cohesive narrative arc across all pages."
    )

    user_prompt = (
        f"Write a story for a {age}-year-old named {name} who enjoys {interests}. "
        f"The story must have exactly {length} vivid, sequential paragraphs."
    )

    result = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ])

    print("[story_agent] LLM Result:", result.content)

    # ✅ Safely split and handle empty output
    pages = [p.strip() for p in result.content.split("\n\n") if p.strip()]
    if not pages:
        raise ValueError("No story content returned from model.")

    state["story_pages"] = pages[:length]
    state["context"] = {
        "name": name,
        "age": age,
        "gender": gender,
        "interests": interests
    }

    print("[story_agent] Returning updated state:", state)
    return state

# ✅ Wrap with RunnableLambda for LangGraph compatibility
story_agent = RunnableLambda(generate_story)
