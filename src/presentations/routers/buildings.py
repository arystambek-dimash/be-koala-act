from typing import List

from fastapi import APIRouter, Depends

from src.app.constants import SubjectEnum
from src.controllers.buildings import BuildingController
from src.presentations.depends import (
    get_current_user,
    get_building_controller, require_admin
)
from src.presentations.schemas.castles import BuildingCreate, BuildingRead, BuildingWithPassagesRead

router = APIRouter(prefix="/buildings", tags=["Buildings"])


# --- Public Routes (Read only) ---
@router.get("", response_model=List[BuildingRead])
async def list_buildings(
        controller: BuildingController = Depends(get_building_controller),
        _=Depends(get_current_user),
):
    return await controller.get_buildings()


# --- Admin Routes (CRUD) ---
@router.post("", response_model=BuildingRead)
async def create_building(
        body: BuildingCreate,
        controller: BuildingController = Depends(get_building_controller),
        _=Depends(require_admin),
):
    return await controller.create_building(body=body)


@router.put("/{building_id}", response_model=BuildingRead)
async def update_building(
        building_id: int,
        body: BuildingCreate,
        controller: BuildingController = Depends(get_building_controller),
        _=Depends(require_admin),
):
    return await controller.update_castle(building_id=building_id, body=body)


@router.delete("/{building_id}")
async def delete_building(
        building_id: int,
        controller: BuildingController = Depends(get_building_controller),
        _=Depends(require_admin),
):
    await controller.delete_building(building_id=building_id)


@router.get("/village/{village_id}", response_model=BuildingWithPassagesRead)
async def get_village_building(
        subject: SubjectEnum,
        village_id: int,
        controller: BuildingController = Depends(get_building_controller),
        _=Depends(get_current_user),
):
    return await controller.get_village_building_detailed(
        subject=subject,
        building_id=village_id,
    )
