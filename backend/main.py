from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from langgraph_app import graph
from story_agent import story_agent, generate_enticer
from image_agent import generate_cover_image, generate_page_image

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

# New enticer endpoint
@app.post("/generate-enticer")
async def generate_enticer_only(request: Request):
    data = await request.json()
    print("[main] Enticer generation payload:", data)
    enticer = await generate_enticer(data)
    return {"enticer": enticer}

# Original endpoint (keep for backward compatibility)
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

# Progressive endpoints
@app.post("/generate-story")
async def generate_story_only(request: Request):
    data = await request.json()
    print("[main] Story generation payload:", data)
    result = story_agent.invoke(data)
    print("[main] Story result:", result)
    return {
        "title": result.get("title"),
        "summary": result.get("summary"),
        "story_pages": result.get("story_pages"),
        "character_descriptions": result.get("character_descriptions"),
        "art_style": result.get("art_style"),
        "context": result.get("context")
    }

@app.post("/generate-cover")
async def generate_cover_only(request: Request):
    data = await request.json()
    print("[main] Cover generation payload:", data)
    cover_url = generate_cover_image(data)
    return {"cover_image": cover_url}

@app.post("/generate-page-image")
async def generate_page_image_only(request: Request):
    data = await request.json()
    print("[main] Page image generation payload:", data)
    image_url = generate_page_image(
        text=data["text"],
        cover_image=data["coverImage"],
        page_index=data["pageIndex"],
        character_descriptions=data.get("character_descriptions", {}),
        art_style=data.get("art_style", "whimsical, colorful children's book style"),
        context=data.get("context", {})
    )
    return {"image_url": image_url}