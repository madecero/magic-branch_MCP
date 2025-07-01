from langchain_core.runnables import RunnableLambda

def save_results(story, images):
    return [{"text": s, "image": i} for s, i in zip(story, images)]

memory_agent = RunnableLambda(save_results)