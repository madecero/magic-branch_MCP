import replicate
from langchain_core.runnables import RunnableLambda

def generate_images(state):
    story_chunks = state["story_pages"]
    context = state["context"]
    images = []

    for i, chunk in enumerate(story_chunks):
        prompt = (
            f"Children's book illustration, cohesive with previous content. "
            f"Scene {i+1}: {chunk[:200]}. The character is a {context['age']}-year-old named {context['name']} who enjoys {context['interests']}."
        )
        output = replicate.run(
            "stability-ai/sdxl-turbo",
            input={"prompt": prompt, "width": 1024, "height": 1024, "num_inference_steps": 1}
        )
        images.append(output[0])
    state["images"] = images
    return state

image_agent = RunnableLambda(generate_images)