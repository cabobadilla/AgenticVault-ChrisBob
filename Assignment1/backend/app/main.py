from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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


# In production the React build lives at ./static (Dockerfile copies it there).
# StaticFiles(html=True) returns index.html for unknown paths so React Router works.
if os.path.isdir("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="spa")
