from langgraph.graph import StateGraph, END # pyright: ignore[reportMissingImports]
from story_agent import story_agent
from image_agent import generate_images
from memory_agent import memory_agent

def build_graph():
    builder = StateGraph(dict)  # Use dict, not AppState
    builder.add_node("story", story_agent)
    builder.add_node("image", generate_images)
    builder.add_node("merge", memory_agent)

    builder.add_edge("__start__", "story")
    builder.set_entry_point("story")
    builder.add_edge("story", "image")
    builder.add_edge("image", "merge")
    builder.add_edge("merge", END)

    return builder.compile()

graph = build_graph()