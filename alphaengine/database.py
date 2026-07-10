"""SQLite persistence for AlphaEngine AI ideas feed."""

from __future__ import annotations

import csv
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

DB_NAME = "prophero_ideas.db"

DEFAULT_HACKATHON_CSV = (
    Path(__file__).resolve().parent / "Hackathon (Madrid) - Ideas - Sheet1.csv"
)

ALLOWED_SOURCES = ("Slack", "Hackathon", "AI")


def _db_path() -> Path:
    return Path(__file__).resolve().parent / DB_NAME


@contextmanager
def get_connection() -> Iterable[sqlite3.Connection]:
    path = _db_path()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                source TEXT NOT NULL,
                upvotes INTEGER NOT NULL DEFAULT 0,
                downvotes INTEGER NOT NULL DEFAULT 0,
                score INTEGER GENERATED ALWAYS AS (upvotes - downvotes) STORED,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_ideas_score_created
            ON ideas (score DESC, created_at DESC)
            """
        )


def normalize_source(raw: str | None, default: str = "Slack") -> str:
    if not raw or not str(raw).strip():
        return default
    s = str(raw).strip()
    for allowed in ALLOWED_SOURCES:
        if s.lower() == allowed.lower():
            return allowed
    return default


def add_idea(
    title: str,
    description: str,
    source: str = "Slack",
    *,
    upvotes: int = 0,
    downvotes: int = 0,
    created_at: datetime | None = None,
) -> int:
    src = normalize_source(source)
    ts = created_at
    if ts is None:
        ts = datetime.now(timezone.utc)
    created = ts.strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO ideas (title, description, source, upvotes, downvotes, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (title.strip(), description.strip(), src, upvotes, downvotes, created),
        )
        return int(cur.lastrowid)


def idea_count() -> int:
    init_db()
    with get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) FROM ideas").fetchone()
    return int(row[0]) if row else 0


def seed_from_hackathon_csv(path: Path | None = None) -> int:
    """
    Lee el CSV del hackathon (Title, Description, …) e inserta ideas con source=Hackathon.
    """
    csv_path = path or DEFAULT_HACKATHON_CSV
    if not csv_path.exists():
        return 0
    records: list[dict[str, Any]] = []
    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = (row.get("Title") or "").strip()
            desc = (row.get("Description") or "").strip()
            if not title or not desc:
                continue
            sponsor = (row.get("Sponsor") or "").strip()
            category = (row.get("Category") or "").strip()
            impact = (row.get("Expected Impact") or "").strip()
            team = (row.get("P&T Team") or "").strip()
            extras: list[str] = []
            if sponsor:
                extras.append(f"Sponsor: {sponsor}")
            if category:
                extras.append(f"Categoría: {category}")
            if team:
                extras.append(f"Equipo P&T: {team}")
            if impact:
                extras.append(f"Impacto esperado:\n{impact}")
            if extras:
                desc = desc.rstrip() + "\n\n— " + "\n".join(extras)
            records.append(
                {"title": title, "description": desc, "source": "Hackathon"}
            )
    return bulk_insert_ideas(records)


def list_ideas_ordered() -> list[dict[str, Any]]:
    init_db()
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, title, description, source, upvotes, downvotes, score, created_at
            FROM ideas
            ORDER BY score DESC, upvotes DESC, created_at DESC
            """
        ).fetchall()
    return [dict(r) for r in rows]


def get_idea(idea_id: int) -> dict[str, Any] | None:
    init_db()
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, title, description, source, upvotes, downvotes, score, created_at
            FROM ideas WHERE id = ?
            """,
            (idea_id,),
        ).fetchone()
    return dict(row) if row else None


def upvote(idea_id: int) -> None:
    init_db()
    with get_connection() as conn:
        conn.execute(
            "UPDATE ideas SET upvotes = upvotes + 1 WHERE id = ?",
            (idea_id,),
        )


def downvote(idea_id: int) -> None:
    init_db()
    with get_connection() as conn:
        conn.execute(
            "UPDATE ideas SET downvotes = downvotes + 1 WHERE id = ?",
            (idea_id,),
        )


def top_ideas_by_score(limit: int = 5) -> list[dict[str, Any]]:
    init_db()
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, title, description, source, upvotes, downvotes, score, created_at
            FROM ideas
            ORDER BY score DESC, upvotes DESC, id ASC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def _lower_key_map(rec: dict[str, Any]) -> dict[str, Any]:
    return {str(k).strip().lower(): v for k, v in rec.items()}


def bulk_insert_ideas(records: list[dict[str, Any]]) -> int:
    """Insert many ideas from import dicts (title, description, optional source/upvotes/downvotes)."""
    init_db()
    count = 0
    with get_connection() as conn:
        for raw in records:
            rec = _lower_key_map(raw) if raw else {}
            title = (rec.get("title") or "").strip()
            desc = (rec.get("description") or "").strip()
            if not title or not desc:
                continue
            src = normalize_source(rec.get("source"))
            up = int(rec.get("upvotes") or 0)
            down = int(rec.get("downvotes") or 0)
            conn.execute(
                """
                INSERT INTO ideas (title, description, source, upvotes, downvotes)
                VALUES (?, ?, ?, ?, ?)
                """,
                (title, desc, src, max(0, up), max(0, down)),
            )
            count += 1
    return count
