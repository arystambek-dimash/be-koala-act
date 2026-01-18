from typing import List

from fastapi import APIRouter, Depends

from src.controllers.passages import PassageController
from src.presentations.depends import (
    get_passage_controller, require_admin
)
from src.presentations.schemas.passages import (
    PassageCreate,
    PassageRead,
    PassageUpdate,
    PassageReorder,
)

router = APIRouter(prefix="/passages", tags=["Passages"])


# --- Admin Routes (CRUD) ---
@router.post("", response_model=PassageRead)
async def create_passage(
        body: PassageCreate,
        controller: PassageController = Depends(get_passage_controller),
        _=Depends(require_admin),
):
    passage = await controller.create(body)
    return PassageRead.model_validate(passage)


@router.patch("/{passage_id}", response_model=PassageRead)
async def update_passage(
        passage_id: int,
        body: PassageUpdate,
        controller: PassageController = Depends(get_passage_controller),
        _=Depends(require_admin)
):
    return await controller.update(passage_id, body)


@router.delete("/{passage_id}")
async def delete_passage(
        passage_id: int,
        controller: PassageController = Depends(get_passage_controller),
        _=Depends(require_admin)
):
    await controller.delete(passage_id)


@router.patch("/order/{village_id}", response_model=List[PassageRead])
async def reorder_passage(
        village_id: int,
        data: PassageReorder,
        _=Depends(require_admin),
        controller: PassageController = Depends(get_passage_controller),
):
    return await controller.reorder_passage(village_id, data.passage_id, data.new_index)
