from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

router = APIRouter()

DATA_FILE = Path(__file__).parent.parent / "data" / "feedback.json"


class FeedbackIn(BaseModel):
    project: str
    comment: str = Field(min_length=1, max_length=1000)
    rating: Optional[int] = Field(default=None, ge=1, le=5)


def _load() -> list[dict]:
    if not DATA_FILE.exists():
        return []
    return json.loads(DATA_FILE.read_text())


def _save(entries: list[dict]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(entries, indent=2))


@router.post("/api/feedback", status_code=201)
async def submit_feedback(item: FeedbackIn):
    entries = _load()
    entry = {
        "id": len(entries) + 1,
        "project": item.project,
        "comment": item.comment,
        "rating": item.rating,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    entries.append(entry)
    _save(entries)
    return {"ok": True, "id": entry["id"]}


@router.get("/api/admin/feedback")
async def list_feedback(project: Optional[str] = Query(default=None)):
    entries = _load()
    if project:
        entries = [e for e in entries if e["project"] == project]
    return {"total": len(entries), "feedback": entries}
