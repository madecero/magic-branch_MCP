from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from langgraph_app import graph
from dotenv import load_dotenv

load_dotenv()
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
    try:
        data = await request.json()
        print("[main] Payload:", data)
        result = graph.invoke(data)
        return {"pages": result["image_pages"]}
    except Exception as e:
        print("[main] Error:", e)
        return {"error": str(e)}
