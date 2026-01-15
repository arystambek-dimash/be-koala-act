from typing import List

from fastapi import APIRouter, Depends

from src.controllers import BuildingCollectorController
from src.presentations.depends import (
    get_current_user, get_building_collector_controller,
)
from src.presentations.schemas.collectors import (
    CastleStatus,
    CollectResult,
    TapRequest,
    TapResult,
    VillageStatus,
)

router = APIRouter(prefix="/collectors", tags=["Collectors"])


# --- Castle ---
@router.get("/castle/status", response_model=CastleStatus)
async def get_castle_status(
        controller: BuildingCollectorController = Depends(get_building_collector_controller),
        current_user=Depends(get_current_user),
):
    return await controller.get_status_castle(user_id=current_user.id)


@router.post("/castle/collect", response_model=CollectResult)
async def collect_castle_treasure(
        controller: BuildingCollectorController = Depends(get_building_collector_controller),
        current_user=Depends(get_current_user),
):
    return await controller.collect_treasure_castle(user_id=current_user.id)


@router.post("/castle/tap", response_model=TapResult)
async def tap_castle(
        body: TapRequest,
        controller: BuildingCollectorController = Depends(get_building_collector_controller),
        current_user=Depends(get_current_user),
):
    return await controller.tap_collect(user_id=current_user.id, tapped=body.tapped)


# --- Villages ---
@router.get("/villages", response_model=List[VillageStatus])
async def get_all_villages_status(
        controller: BuildingCollectorController = Depends(get_building_collector_controller),
        current_user=Depends(get_current_user),
):
    return await controller.get_all_villages_statuses(user_id=current_user.id)


@router.get("/villages/{village_id}/status", response_model=VillageStatus)
async def get_village_status(
        village_id: int,
        controller: BuildingCollectorController = Depends(get_building_collector_controller),
        current_user=Depends(get_current_user),
):
    return await controller.get_status_village(
        user_id=current_user.id,
        village_id=village_id,
    )


@router.post("/villages/{village_id}/collect", response_model=CollectResult)
async def collect_village_treasure(
        village_id: int,
        controller: BuildingCollectorController = Depends(get_building_collector_controller),
        current_user=Depends(get_current_user),
):
    return await controller.collect_treasure_village(
        user_id=current_user.id,
        village_id=village_id,
    )
