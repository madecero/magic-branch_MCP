from langchain_core.runnables import RunnableLambda

def save_results(state):
    story = state["story_pages"]
    images = state["images"]
    return [{"text": s, "image": i} for s, i in zip(story, images)]

memory_agent = RunnableLambda(save_results)