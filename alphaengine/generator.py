"""Generate new ideas with Anthropic Claude from top-voted seeds."""

from __future__ import annotations

import json
import os
import re
from typing import Any

from anthropic import Anthropic

from database import add_idea, top_ideas_by_score

DEFAULT_MODEL = "claude-3-5-sonnet-20241022"


def _build_prompt(top_ideas: list[dict[str, Any]]) -> str:
    lines = []
    for i, idea in enumerate(top_ideas, start=1):
        lines.append(
            f"{i}. {idea['title']}: {idea['description']}"
        )
    ideas_block = "\n".join(lines)
    return (
        "Basado en estas ideas exitosas en PropHero: "
        f"[{ideas_block}]\n\n"
        "Genera 3 conceptos nuevos y disruptivos de PropTech. "
        "Devuélveme exclusivamente un JSON array de objetos; cada objeto solo "
        'tiene los campos "title" y "description" (strings). '
        "Sin markdown ni texto fuera del JSON."
    )


def _extract_json_array(text: str) -> list[dict[str, Any]]:
    text = text.strip()
    # Strip optional ```json ... ``` fences
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if fence:
        text = fence.group(1).strip()
    data = json.loads(text)
    if not isinstance(data, list):
        raise ValueError("La respuesta no es un JSON array")
    out: list[dict[str, Any]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        desc = str(item.get("description", "")).strip()
        if title and desc:
            out.append({"title": title, "description": desc})
    if not out:
        raise ValueError("No se pudo parsear ninguna idea válida del JSON.")
    return out[:3]


def generate_and_store_ai_ideas(
    *,
    api_key: str | None = None,
    model: str | None = None,
    top_n: int = 5,
) -> list[int]:
    """
    Toma las ``top_n`` ideas con mayor score, llama a Claude y persiste 3 ideas con source='AI'.

    Returns lista de ids insertados.
    """
    seeds = top_ideas_by_score(limit=top_n)
    if not seeds:
        raise ValueError("No hay ideas en la base de datos; importa o crea ideas primero.")

    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise ValueError("Falta ANTHROPIC_API_KEY en el entorno o como argumento.")

    client = Anthropic(api_key=key)
    use_model = model or os.environ.get("ANTHROPIC_MODEL", DEFAULT_MODEL)
    user_prompt = _build_prompt(seeds)

    message = client.messages.create(
        model=use_model,
        max_tokens=2048,
        temperature=0.9,
        messages=[{"role": "user", "content": user_prompt}],
    )

    text_parts: list[str] = []
    for block in message.content:
        txt = getattr(block, "text", None)
        if isinstance(txt, str) and txt:
            text_parts.append(txt)
    raw = "".join(text_parts).strip()

    parsed = _extract_json_array(raw)
    if not parsed:
        raise ValueError("Claude no devolvió ideas parseables.")
    ids: list[int] = []
    for item in parsed:
        ids.append(
            add_idea(
                item["title"],
                item["description"],
                source="AI",
            )
        )
    return ids
