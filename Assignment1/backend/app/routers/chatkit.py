from __future__ import annotations

import json
import os
import uuid
from typing import Any, Mapping

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

_CHATKIT_BASE = "https://api.openai.com"
_COOKIE_NAME = "chatkit_session_id"
_COOKIE_MAX_AGE = 60 * 60 * 24 * 30  # 30 days


@router.post("/api/create-session")
async def create_session(request: Request) -> JSONResponse:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _respond({"error": "Missing OPENAI_API_KEY environment variable"}, 500)

    body = await _read_json(request)
    workflow_id = _resolve_workflow(body)
    if not workflow_id:
        return _respond({"error": "Missing workflow id"}, 400)

    user_id, new_cookie = _resolve_user(request.cookies)
    api_base = os.getenv("CHATKIT_API_BASE") or _CHATKIT_BASE

    try:
        async with httpx.AsyncClient(base_url=api_base, timeout=10.0) as client:
            upstream = await client.post(
                "/v1/chatkit/sessions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "OpenAI-Beta": "chatkit_beta=v1",
                    "Content-Type": "application/json",
                },
                json={"workflow": {"id": workflow_id}, "user": user_id},
            )
    except httpx.RequestError as exc:
        return _respond({"error": f"Failed to reach ChatKit API: {exc}"}, 502, new_cookie)

    payload = _parse_json(upstream)
    if not upstream.is_success:
        msg = (payload.get("error") if isinstance(payload, Mapping) else None) or upstream.reason_phrase
        return _respond({"error": msg or "Upstream error"}, upstream.status_code, new_cookie)

    client_secret = payload.get("client_secret") if isinstance(payload, Mapping) else None
    if not client_secret:
        return _respond({"error": "Missing client_secret in upstream response"}, 502, new_cookie)

    return _respond(
        {"client_secret": client_secret, "expires_after": payload.get("expires_after")},
        200,
        new_cookie,
    )


def _respond(payload: Mapping[str, Any], status: int, cookie: str | None = None) -> JSONResponse:
    response = JSONResponse(payload, status_code=status)
    if cookie:
        is_prod = (os.getenv("ENVIRONMENT") or "").lower() == "production"
        response.set_cookie(
            key=_COOKIE_NAME,
            value=cookie,
            max_age=_COOKIE_MAX_AGE,
            httponly=True,
            samesite="lax",
            secure=is_prod,
        )
    return response


async def _read_json(request: Request) -> Mapping[str, Any]:
    raw = await request.body()
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, Mapping) else {}
    except json.JSONDecodeError:
        return {}


def _resolve_workflow(body: Mapping[str, Any]) -> str | None:
    wf = body.get("workflow", {})
    wf_id = (wf.get("id") if isinstance(wf, Mapping) else None) or body.get("workflowId")
    wf_id = wf_id or os.getenv("CHATKIT_WORKFLOW_ID") or os.getenv("VITE_CHATKIT_WORKFLOW_ID")
    return wf_id.strip() if wf_id and isinstance(wf_id, str) and wf_id.strip() else None


def _resolve_user(cookies: Mapping[str, str]) -> tuple[str, str | None]:
    existing = cookies.get(_COOKIE_NAME)
    if existing:
        return existing, None
    new_id = str(uuid.uuid4())
    return new_id, new_id


def _parse_json(response: httpx.Response) -> Mapping[str, Any]:
    try:
        parsed = response.json()
        return parsed if isinstance(parsed, Mapping) else {}
    except Exception:
        return {}
