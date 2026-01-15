from fastapi import APIRouter, Depends

from src.app.constants import SubjectEnum
from src.controllers.building_progression import BuildingProgressionController
from src.presentations.depends import (
    get_current_user,
    get_building_progression_controller,
)
from src.presentations.schemas.collectors import UpgradeInfo, UpgradeResult

router = APIRouter(prefix="/progression", tags=["Progression"])


# --- Castle Progression ---
@router.get("/castle/upgrade-info", response_model=UpgradeInfo)
async def get_castle_upgrade_info(
        controller: BuildingProgressionController = Depends(get_building_progression_controller),
        current_user=Depends(get_current_user),
):
    return await controller.get_castle_upgrade_info(user_id=current_user.id)


@router.post("/castle/upgrade", response_model=UpgradeResult)
async def upgrade_castle(
        controller: BuildingProgressionController = Depends(get_building_progression_controller),
        current_user=Depends(get_current_user),
):
    return await controller.upgrade_castle(user_id=current_user.id)


# --- Village Progression ---
@router.get("/villages/{subject}/upgrade-info", response_model=UpgradeInfo)
async def get_village_upgrade_info(
        subject: SubjectEnum,
        controller: BuildingProgressionController = Depends(get_building_progression_controller),
        current_user=Depends(get_current_user),
):
    return await controller.get_village_upgrade_info(user_id=current_user.id, subject=subject)


@router.post("/villages/{subject}/upgrade", response_model=UpgradeResult)
async def upgrade_village(
        subject: SubjectEnum,
        controller: BuildingProgressionController = Depends(get_building_progression_controller),
        current_user=Depends(get_current_user),
):
    return await controller.upgrade_village(user_id=current_user.id, subject=subject)
