# Multi-Agent Research Pipeline

A multi-agent research pipeline built with LangChain/LangGraph: a search agent finds sources, a reader agent scrapes and digests them, and (defined but not yet wired in) a writer/critic pair can turn the notes into a fact-checked article. Exposed over FastAPI with a React frontend.

## Pipeline overview

```
Topic
  │
  ▼
[agent.py] search agent (ReAct, tool: web_search)
  │   Tavily search → titles/URLs/snippets
  ▼
[agent.py] reader agent (ReAct, tool: scrape_url)
  │   picks relevant URLs from search results, scrapes them, summarizes into notes
  ▼
[pipeline.py] combines search_results + reader_results → research
  │
  ▼
state = { search_results, reader_results, research }
```

- `tools.py` — `web_search` (Tavily search, returns title/URL/snippet per result) and `scrape_url` (fetches a URL with `requests`/`BeautifulSoup`, strips scripts/nav/footer, returns up to 3000 chars of clean text).
- `agent.py` — configures Gemini through `ChatGoogleGenerativeAI` and defines the planner, search and reader agents, writer, critic, and revision chains.
- `pipeline.py` — `run_research_pipeline(topic)` runs the search agent, then the reader agent on its output, and combines both into a `research` string.
- `server.py` — FastAPI app exposing `POST /api/research`, CORS-enabled for `http://localhost:5173`.
- `frontend/` — React (Vite) single-page app: enter a topic, view search results, reader notes, and combined research.

## API

| Method | Route            | Body                     | Description                                                                 |
|--------|------------------|---------------------------|-------------------------------------------------------------------------------|
| POST   | `/api/research`  | JSON `{ "topic": string }` | Runs the search + reader agents for the topic. Returns `{ search_results, reader_results, research }`. |

Note: there's no persistence — each request re-runs the full pipeline synchronously, which can take a while (multiple LLM + tool calls).

## Setup

### Backend

1. Create a `.env` file in this folder with:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the API:
   ```bash
   python -m uvicorn server:app --reload
   ```
   Serves at `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Serves at `http://localhost:5173` (default Vite port) and talks to the API at `http://localhost:8000` (hardcoded in `frontend/src/App.jsx`).

## Usage

1. Start the backend (`uvicorn server:app --reload`) and frontend (`npm run dev`).
2. Open the frontend, enter a research topic, and click Run.
3. Wait for the search and reader agents to finish — results are shown as three panels: search results, reader notes, and combined research.

You can also run the pipeline standalone from the command line:
```bash
python pipeline.py
```

## Tech stack

- **Backend**: FastAPI, LangChain, LangGraph (`create_agent`)
- **LLM**: Google Gemini (`gemini-3.5-flash-lite` by default, configurable with `GEMINI_MODEL`)
- **Tools**: Tavily (web search), `requests` + BeautifulSoup (scraping)
- **Frontend**: React 19 + Vite
