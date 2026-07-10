"""AlphaEngine AI — FastAPI + HTML simple."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import database as db
from generator import generate_and_store_ai_ideas

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(BASE_DIR / ".env")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    db.init_db()
    if db.idea_count() == 0:
        db.seed_from_hackathon_csv()
    yield


app = FastAPI(title="AlphaEngine AI", lifespan=lifespan)
app.mount("/assets", StaticFiles(directory=BASE_DIR / "assets"), name="assets")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
def home(request: Request, gen: str | None = None):
    ideas = db.list_ideas_ordered()
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "ideas": ideas,
            "has_anthropic": bool(os.environ.get("ANTHROPIC_API_KEY")),
            "gen": gen,
        },
    )


@app.post("/ideas/{idea_id}/upvote")
def upvote(idea_id: int):
    db.upvote(idea_id)
    return RedirectResponse(url="/", status_code=303)


@app.post("/ideas/{idea_id}/downvote")
def downvote(idea_id: int):
    db.downvote(idea_id)
    return RedirectResponse(url="/", status_code=303)


@app.post("/generate")
def generate():
    try:
        generate_and_store_ai_ideas()
        return RedirectResponse(url="/?gen=ok", status_code=303)
    except Exception:
        return RedirectResponse(url="/?gen=err", status_code=303)
