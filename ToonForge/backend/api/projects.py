from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
import tempfile
import os

from services.project_service import ProjectService
from models.schemas import Project

router = APIRouter()
service = ProjectService("_projects")


@router.get("/", response_model=List[Project])
async def list_projects():
    return service.list_projects()


@router.post("/", response_model=Project)
async def create_project(name: str = Form("New Project")):
    return service.create_project(name)


@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: str):
    project = service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/import/audio", response_model=Project)
async def import_audio(project_id: str, files: List[UploadFile] = File(...)):
    temp_paths = []
    orig_names = []
    try:
        for f in files:
            tmp = tempfile.NamedTemporaryFile(delete=False)
            tmp.write(await f.read())
            tmp.flush()
            temp_paths.append(tmp.name)
            orig_names.append(f.filename)
        service.import_audio(project_id, temp_paths, orig_names)
        project = service.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    finally:
        for p in temp_paths:
            try:
                os.unlink(p)
            except OSError:
                pass


@router.post("/{project_id}/import/characters", response_model=Project)
async def import_characters(project_id: str, files: List[UploadFile] = File(...)):
    temp_paths = []
    orig_names = []
    try:
        for f in files:
            tmp = tempfile.NamedTemporaryFile(delete=False)
            tmp.write(await f.read())
            tmp.flush()
            temp_paths.append(tmp.name)
            orig_names.append(f.filename)
        service.import_characters(project_id, temp_paths, orig_names)
        project = service.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    finally:
        for p in temp_paths:
            try:
                os.unlink(p)
            except OSError:
                pass


@router.post("/{project_id}/import/background", response_model=Project)
async def import_background(project_id: str, file: UploadFile = File(...)):
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.write(await file.read())
    tmp.flush()
    try:
        service.import_background(project_id, tmp.name, file.filename)
        project = service.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    finally:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass


@router.put("/{project_id}", response_model=Project)
async def update_project(project_id: str, project: Project):
    project.id = project_id
    service.save_project(project)
    updated = service.get_project(project_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated
