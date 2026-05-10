import os
import threading
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from models.schemas import ExportRequest, ExportFormat
from services.project_service import ProjectService
from core.scene_orchestrator import SceneOrchestrator
from core.render_engine import RenderEngine

router = APIRouter()
project_service = ProjectService("_projects")
render_engine = RenderEngine()

_render_status: dict[str, dict] = {}


@router.post("/export")
async def export_scene(request: ExportRequest):
    project = project_service.get_project(request.scene_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    output_path = request.output_path or os.path.join(
        "_projects", request.scene_id, "output",
        f"export_{request.format.value}.mp4"
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    orchestrator = SceneOrchestrator(
        os.path.join("_projects", request.scene_id)
    )
    manifest = orchestrator.build_scene_manifest(project)

    thread_id = request.scene_id
    _render_status[thread_id] = {"status": "rendering", "progress": 0}

    def render_thread():
        try:
            def on_progress(pct: int):
                _render_status[thread_id] = {"status": "rendering", "progress": pct}
            render_engine.set_progress_callback(on_progress)
            result = render_engine.render_manifest(
                manifest, output_path,
                fmt=request.format,
                include_subtitles=request.include_subtitles,
                quality=request.quality,
            )
            _render_status[thread_id] = {"status": "completed", "output": result}
        except Exception as e:
            _render_status[thread_id] = {"status": "failed", "error": str(e)}

    thread = threading.Thread(target=render_thread, daemon=True)
    thread.start()

    return {
        "status": "started",
        "render_id": thread_id,
        "output_path": output_path,
    }


@router.get("/status/{render_id}")
async def render_status(render_id: str):
    status = _render_status.get(render_id)
    if not status:
        raise HTTPException(status_code=404, detail="Render job not found")
    return status


@router.get("/download/{project_id}/{filename}")
async def download_export(project_id: str, filename: str):
    filepath = os.path.join("_projects", project_id, "output", filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(filepath, media_type="video/mp4", filename=filename)
