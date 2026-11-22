from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.genai.errors import APIError
from pydantic import BaseModel

from pipeline import run_research_pipeline

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResearchRequest(BaseModel):
    topic: str


@app.post("/api/research")
def research(request: ResearchRequest):
    try:
        return run_research_pipeline(request.topic)
    except APIError as error:
        if error.code != 429:
            raise

        headers = None
        if error.response:
            retry_after = error.response.headers.get("Retry-After")
            if retry_after:
                headers = {"Retry-After": retry_after}

        raise HTTPException(
            status_code=429,
            detail=(
                "Gemini's rate limit was reached. Wait before trying again. "
                "If it persists, check your Gemini API quota."
            ),
            headers=headers,
        ) from error
