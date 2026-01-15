from fastapi import APIRouter, Depends

from src.controllers.passages import PassageController
from src.presentations.depends import (
    get_passage_controller, require_admin
)
from src.presentations.schemas.passages import (
    PassageCreate,
    PassageRead,
    PassageUpdate,
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
    print(passage.id)
    return PassageRead.from_orm(passage)


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
