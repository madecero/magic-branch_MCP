from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda

from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(model="gpt-4", temperature=0.8)

def generate_story(data):
    name = data.get("name", "the child")
    gender = data.get("gender", "neutral")
    age = data.get("age", 4)
    interests = ", ".join(data.get("interests", []))
    length = data.get("length", 5)

    system_prompt = (
        "You are a friendly storybook AI that creates short, vivid, age-appropriate stories for children. "
        "Generate exactly {length} story pages. Each page should be a clear and complete paragraph. "
        "Avoid headings like 'Page 1'. Do not leave any page empty. Each paragraph should be fun, simple, and imaginative."
        "The main character of the story is a child named {name} who is {age} years old and enjoys {interests}."
        "The child should get a sense that magic is real from the story."
    ).format(length=length, name=name, age=age, interests=interests)

    user_prompt = (
        f"Write a children's story for a {age}-year-old named {name} who enjoys {interests}. "
        f"Make the story {length} pages long. Each page should be a warm, engaging paragraph."
    )

    result = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ])

    pages = [p.strip() for p in result.content.split("\n\n") if p.strip()]
    return pages[:length]

story_agent = RunnableLambda(generate_story)