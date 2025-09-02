## Frontend (Next.js) – Story & Illustration Generator UI

This frontend provides a progressive experience for generating a personalized children's story and its accompanying illustrations. It talks to the FastAPI backend (default: `http://localhost:8000`) which orchestrates LangGraph story + image generation.

### Features
- Progressive generation (story -> cover -> page illustrations) with live status updates.
- Smooth page reveal UX with Framer Motion.
- Toast feedback (`react-hot-toast`).
- Swipeable reading view (mobile friendly via `react-swipeable`).

### Tech Stack
Next.js 15 (Pages Router), React 19, TypeScript, Tailwind CSS 4 (PostCSS pipeline), Framer Motion, Axios.

### Prerequisites
- Node.js 18+ (or 20+ recommended)
- Backend running locally on port 8000 (see `../backend/README.md`).

### Install & Run
```bash
npm install
npm run dev
```
Visit: http://localhost:3000

### Configuration
Currently the API base URL is hard‑coded in `utils/api.ts` as `http://localhost:8000`.
Optionally you can refactor to use an environment variable:
1. Create `./.env.local`
2. Add: `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`
3. Update `utils/api.ts` to read `process.env.NEXT_PUBLIC_API_BASE_URL`.

### Code Map
- `pages/index.tsx` – Main UI & orchestration.
- `components/StoryForm.tsx` – User input form (name, age, interests, length).
- `components/GenerationProgress.tsx` – Live status + incremental page reveal.
- `utils/api.ts` – Progressive generation workflow logic.
- `types/` – Shared TypeScript types.

### Data Flow (Progressive Generation)
1. POST `/generate-story` – Retrieves title, summary, story pages, character metadata.
2. POST `/generate-cover` – Generates a single portrait cover image.
3. Parallel POST `/generate-page-image` per story page – Adds illustrations.
4. UI updates as each page arrives.

### Development Tips
- Adjust animation timings in `GenerationProgress.tsx` if adding more steps.
- Guard against duplicate page order by relying on the original story page index (currently sorting by original array position).
- If you introduce server-side rendering or streaming, move generation logic to API routes or React Server Actions.

### Production Build
```bash
npm run build
npm start
```

### Linting
```bash
npm run lint
```

### Extending
- Add theme selector (fairytale / sci‑fi) -> pass extra prompt context to backend.
- Introduce caching layer for identical prompts (e.g., Redis) to avoid re-generation.
- Add download-as-PDF (collect pages + images, render via `pdf-lib`).

### Learn More (Next.js Resources)
- https://nextjs.org/docs
- https://nextjs.org/learn-pages-router

### Deployment
Can be deployed to Vercel or any Node hosting. Ensure environment variable for the backend API base (if refactored) is configured.

---
Generated from the original Create Next App template and customized for the LangGraph Story Generation project.
