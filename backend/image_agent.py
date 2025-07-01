from langchain_core.runnables import RunnableLambda

def generate_images(state):
    print("[image_agent] Received state:", state)

    story_chunks = state.get("story_pages")
    if not story_chunks:
        raise ValueError("Missing story_pages in state.")

    # Stubbed image generation
    image_urls = [f"https://dummyimage.com/600x400/000/fff&text=Page+{i+1}" for i in range(len(story_chunks))]
    state["image_pages"] = [
        {"text": chunk, "image_url": image_urls[i]} for i, chunk in enumerate(story_chunks)
    ]
    return state

generate_images = RunnableLambda(generate_images)