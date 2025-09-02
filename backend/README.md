# Backend (FastAPI + LangGraph)

This service powers the story + illustration generation pipeline consumed by the Next.js frontend.

## Overview
Pipeline (LangGraph state machine):
1. story (LLM authored JSON: title, summary, pages, characters, art style)
2. image (cover + per-page illustrations in parallel)
3. merge (currently identity; future: persistence / memory)

Endpoints (FastAPI):
- `POST /generate` (legacy combined flow via LangGraph `ainvoke`)
- `POST /generate-story` (story metadata only)
- `POST /generate-cover` (single cover image)
- `POST /generate-page-image` (one page illustration)
- `GET /` (healthcheck)

## Tech Stack
- FastAPI
- LangGraph + LangChain
- OpenAI (GPT-4 + DALL·E 3)
- Python 3.11+
- Async image generation (parallel via `asyncio.gather`)

## File Map
- `main.py` – FastAPI app + endpoints
- `langgraph_app.py` – Graph construction
- `story_agent.py` – Story JSON generation & parsing
- `image_agent.py` – Cover + page prompts and DALL·E calls
- `memory_agent.py` – Placeholder node (future user memory store)

## Installation
Create & activate a virtual environment (recommended):
```
python -m venv .venv
.venv\Scripts\activate  # Windows
```
Install dependencies:
```
pip install -r requirements.txt
```

## Environment Variables
Create a `.env` file in project root (same level as `requirements.txt`):
```
OPENAI_API_KEY=sk-...
```
(Any other provider keys can be added later.)

## Run the Server
Development (auto-reload):
```
uvicorn backend.main:app --reload --port 8000
```
Then visit: http://localhost:8000

## Flow Details
### Story Generation
`story_agent.generate_story` enforces strict JSON output. Fallback logic creates a basic 5-paragraph story if parsing fails. State includes:
```
{
  title, summary, story_pages[], character_descriptions{}, art_style, context{}
}
```

### Image Generation
`image_agent.generate_cover_image` + `generate_page_image` craft prompts with:
- Portrait orientation enforcement (1024x1792)
- Zero text policy
- Consistent character appearance
- Reserved lower third for overlay (future use)

Page images execute in parallel (`asyncio.gather`) for responsiveness.

## Error Handling
- JSON parsing fallback in `story_agent`
- DALL·E exceptions => placeholder dummyimage.com URL
- Missing `story_pages` => raises `ValueError`

## Extensibility Ideas
- Add persistence layer for stories (PostgreSQL / Redis)
- Add auth & per-user memory in `memory_agent`
- Streaming token-wise story generation
- Caching identical page prompts
- Support alternate image models (Replicate / Stability)

## Testing Quick Check
Manual curl examples:
```
curl -X POST http://localhost:8000/generate-story -H "Content-Type: application/json" -d "{\"name\":\"Ava\",\"gender\":\"girl\",\"age\":5,\"interests\":[\"dragons\"],\"length\":5}"
```
Then use returned JSON to request cover + page images.

## License
Internal / TBD.
