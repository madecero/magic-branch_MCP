from langgraph.graph import StateGraph, END
from story_agent import story_agent
from image_agent import image_agent
from memory_agent import memory_agent

class AppState(dict):
    pass

def build_graph():
    builder = StateGraph(AppState)
    builder.add_node("story", story_agent)
    builder.add_node("image", image_agent)
    builder.add_node("merge", memory_agent)

    builder.set_entry_point("story")
    builder.add_edge("story", "image")
    builder.add_edge("image", "merge")
    builder.add_edge("merge", END)

    return builder.compile()

graph = build_graph()