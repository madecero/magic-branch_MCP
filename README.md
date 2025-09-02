# LangGraph Story Illustration App

Full-stack application that generates personalized children's stories and matching illustrations using OpenAI models orchestrated through a LangGraph pipeline.

## Architecture Summary
```
Root
├── backend/   (FastAPI + LangGraph; story + image generation)
├── frontend/  (Next.js UI; progressive generation experience)
└── requirements.txt (Python deps)
```

### Generation Flow
1. User submits: name, age, gender, interests, desired length.
2. Backend story node (`story_agent`) returns structured JSON (title, summary, pages, character descriptions, art style).
3. Cover image created (`generate_cover_image`).
4. Page illustrations dispatched in parallel (`generate_page_image`).
5. Frontend reveals pages progressively as each image returns.

## Repos & Tech
- Python 3.11+, FastAPI, LangChain / LangGraph
- OpenAI GPT-4 (story JSON) + DALL·E 3 (images 1024x1792 portrait)
- Next.js 15 (Pages Router), React 19, TypeScript, Tailwind CSS 4
- Animation & UX: Framer Motion, react-swipeable, react-hot-toast

## Local Setup
### 1. Backend
```
python -m venv .venv
.venv\\Scripts\\activate  # Windows
pip install -r requirements.txt
# .env file with OPENAI_API_KEY=sk-...
uvicorn backend.main:app --reload --port 8000
```
Health: http://localhost:8000

### 2. Frontend
```
cd frontend
npm install
npm run dev
```
Visit: http://localhost:3000

## Key Directories
- `backend/story_agent.py` – LLM prompt + JSON parsing + fallback
- `backend/image_agent.py` – Prompt engineering for cover & pages (portrait enforcement)
- `backend/langgraph_app.py` – StateGraph wiring (story -> image -> merge)
- `backend/main.py` – FastAPI endpoints (granular + legacy)
- `frontend/components/` – Form + generation progress UI
- `frontend/utils/api.ts` – Progressive generation client workflow

## Environment Variables
Create `.env` at project root:
```
OPENAI_API_KEY=sk-...
```
(Frontend currently uses static backend URL; can be refactored to `NEXT_PUBLIC_API_BASE_URL`.)

## API Overview
| Endpoint | Purpose |
|----------|---------|
| POST /generate-story | Story metadata (no images) |
| POST /generate-cover | Cover image only |
| POST /generate-page-image | Single page illustration |
| POST /generate | Legacy combined graph call |
| GET / | Healthcheck |

## Error & Resilience Notes
- Story JSON parse failure => fallback story pages
- Image generation failure => red placeholder image URL
- Parallel page generation improves perceived speed

## Roadmap Ideas
- Persistence (DB) & user accounts
- Streaming story creation (token-level updates)
- Alternate image pipelines (Stability, Flux, SDXL) with style options
- Caching identical prompt results
- Export: PDF / EPUB builder

## Contributing
PRs welcome. Keep prompts concise, enforce portrait constraints, and document new graph nodes in `backend/README.md`.

## License
TBD
