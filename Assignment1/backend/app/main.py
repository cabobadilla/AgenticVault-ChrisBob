from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.routers import chatkit, feedback

app = FastAPI(title="AI Bootcamp Portfolio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chatkit.router)
app.include_router(feedback.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


# In production, the React build lives at ./static (Dockerfile copies it there).
# Vite outputs JS/CSS bundles to ./static/assets/ — mount that sub-path directly.
# A catch-all route serves index.html for every other path so React Router works
# on direct navigation and browser refresh (StaticFiles(html=True) alone does NOT
# do SPA fallback — it only serves index.html when a directory is requested).
if os.path.isdir("static/assets"):
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")


@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    static_file = f"static/{full_path}"
    if os.path.isfile(static_file):
        return FileResponse(static_file)
    if os.path.isfile("static/index.html"):
        return FileResponse("static/index.html")
    raise HTTPException(status_code=404, detail="Not Found")
