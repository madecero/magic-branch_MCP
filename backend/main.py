from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from langgraph_app import graph

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def healthcheck():
    return {"status": "ok"}

@app.post("/generate")
async def generate_story_and_images(request: Request):
    data = await request.json()
    print("[main] Payload:", data)
    if hasattr(graph, "ainvoke"):
        result = await graph.ainvoke(data)
    else:
        result = graph.invoke(data)
    print("[main] Result:", result)
    return {"pages": result.get("image_pages", [])}