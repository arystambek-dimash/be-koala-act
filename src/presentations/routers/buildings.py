from typing import List

from fastapi import APIRouter, Depends

from src.app.constants import SubjectEnum, BuildingType
from src.controllers.buildings import BuildingController
from src.presentations.depends import (
    get_current_user,
    get_building_controller, require_admin
)
from src.presentations.schemas.buildings import (
    BuildingWithPassagesRead,
    BuildingCastleRead,
    BuildingVillageRead,
    BuildingCastleUserRead,
    BuildingVillageUserRead,
    BuildingCastleCreate,
    BuildingVillageCreate,
    BuildingUpdate,
)

router = APIRouter(prefix="/buildings", tags=["Buildings"])


@router.get("/castles", response_model=List[BuildingCastleUserRead])
async def list_castles(
        controller: BuildingController = Depends(get_building_controller),
        current_user=Depends(get_current_user),
):
    return await controller.list_buildings(BuildingType.CASTLE, user_id=current_user.id)


@router.get("/villages", response_model=List[BuildingVillageUserRead])
async def list_villages(
        subject: SubjectEnum,
        controller: BuildingController = Depends(get_building_controller),
        current_user=Depends(get_current_user),
):
    return await controller.list_buildings(BuildingType.VILLAGE, user_id=current_user.id, subject=subject)


# --- Admin Routes (CRUD) ---

@router.post("/castles", response_model=BuildingCastleRead)
async def create_castle(
        body: BuildingCastleCreate,
        controller: BuildingController = Depends(get_building_controller),
        _=Depends(require_admin),
):
    return await controller.create_building(body=body, building_type=BuildingType.CASTLE)


@router.post("/villages", response_model=BuildingVillageRead)
async def create_village(
        body: BuildingVillageCreate,
        controller: BuildingController = Depends(get_building_controller),
        _=Depends(require_admin),
):
    return await controller.create_building(body=body, building_type=BuildingType.VILLAGE)


@router.put("/castles/{building_id}", response_model=BuildingCastleRead)
async def update_castle(
        building_id: int,
        body: BuildingUpdate,
        controller: BuildingController = Depends(get_building_controller),
        _=Depends(require_admin),
):
    return await controller.update_building(
        building_id=building_id,
        body=body,
        building_type=BuildingType.CASTLE
    )


@router.put("/villages/{building_id}", response_model=BuildingVillageRead)
async def update_village(
        building_id: int,
        body: BuildingUpdate,
        controller: BuildingController = Depends(get_building_controller),
        _=Depends(require_admin),
):
    return await controller.update_building(
        building_id=building_id,
        body=body,
        building_type=BuildingType.VILLAGE
    )


@router.delete("/{building_id}")
async def delete_building(
        building_id: int,
        controller: BuildingController = Depends(get_building_controller),
        _=Depends(require_admin),
):
    await controller.delete_building(building_id=building_id)


@router.get("/village/{village_id}", response_model=BuildingWithPassagesRead)
async def get_village_building(
        village_id: int,
        controller: BuildingController = Depends(get_building_controller),
        _=Depends(get_current_user),
):
    return await controller.get_village_with_passages(
        building_id=village_id,
    )


@router.get("/admin/castles", response_model=List[BuildingCastleRead])
async def admin_list_castles(
        controller: BuildingController = Depends(get_building_controller),
        _=Depends(require_admin),
):
    return await controller.admin_list_buildings(BuildingType.CASTLE)


@router.get("/admin/villages", response_model=List[BuildingVillageRead])
async def admin_list_villages(
        subject: SubjectEnum,
        controller: BuildingController = Depends(get_building_controller),
        _=Depends(require_admin),
):
    return await controller.admin_list_buildings(BuildingType.VILLAGE, subject)
