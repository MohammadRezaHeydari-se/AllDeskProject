import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api import projects, scenes, render, characters, audio

app = FastAPI(title="ToonForge", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_projects_dir = os.path.join(os.path.dirname(__file__), "_projects")
os.makedirs(_projects_dir, exist_ok=True)
if os.path.isdir(_projects_dir):
    app.mount("/_projects", StaticFiles(directory=_projects_dir), name="projects")

app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(characters.router, prefix="/api/characters", tags=["characters"])
app.include_router(audio.router, prefix="/api/audio", tags=["audio"])
app.include_router(scenes.router, prefix="/api/scenes", tags=["scenes"])
app.include_router(render.router, prefix="/api/render", tags=["render"])

@app.get("/api/health")
async def health():
    return {"status": "ok", "app": "ToonForge"}
