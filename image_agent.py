import replicate
from langchain_core.runnables import RunnableLambda

def generate_images(story_chunks):
    images = []
    for chunk in story_chunks:
        prompt = f"Children's book illustration: {chunk[:200]}"
        output = replicate.run(
            "stability-ai/sdxl-turbo",
            input={"prompt": prompt, "width": 1024, "height": 1024, "num_inference_steps": 1}
        )
        images.append(output[0])
    return images

image_agent = RunnableLambda(generate_images)