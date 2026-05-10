from fastapi import APIRouter, HTTPException
from models.schemas import Project, MappingOverride
from services.project_service import ProjectService
from core.scene_orchestrator import SceneOrchestrator

router = APIRouter()
project_service = ProjectService("_projects")


@router.post("/generate/{project_id}")
async def generate_scene(project_id: str):
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    orchestrator = SceneOrchestrator(
        f"_projects/{project_id}"
    )
    project = orchestrator.scan_assets(existing_project=project)
    project_service.save_project(project)
    return project


@router.post("/mapping/{project_id}")
async def update_mapping(project_id: str, overrides: list[MappingOverride]):
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    orchestrator = SceneOrchestrator(
        f"_projects/{project_id}"
    )
    project = orchestrator.update_mapping(project, overrides)
    project_service.save_project(project)
    return project


@router.get("/manifest/{project_id}")
async def get_manifest(project_id: str):
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    orchestrator = SceneOrchestrator(
        f"_projects/{project_id}"
    )
    manifest = orchestrator.build_scene_manifest(project)
    return manifest
