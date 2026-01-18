from typing import Optional

from fastapi import APIRouter, Depends

from src.controllers.passage_nodes import PassageNodeController
from src.presentations.depends import (
    get_passage_node_controller, require_admin,
)
from src.presentations.schemas.nodes import (
    BossNodeCreate,
    BossNodeUpdate,
    BossNodeRead,
)

router = APIRouter(prefix="/boss", tags=["Node Bosses"])


@router.post("", response_model=BossNodeRead, description="Create a boss node for passage")
async def create_boss(
        passage_id: int,
        body: BossNodeCreate,
        controller: PassageNodeController = Depends(get_passage_node_controller),
        _=Depends(require_admin),
):
    return await controller.create_boss(passage_id, body)


@router.patch("/{node_id}", response_model=BossNodeRead)
async def update_boss(
        node_id: int,
        body: BossNodeUpdate,
        controller: PassageNodeController = Depends(get_passage_node_controller),
        _=Depends(require_admin),
):
    return await controller.update_boss(node_id, body)


@router.delete("/{node_id}")
async def delete_node(
        node_id: int,
        controller: PassageNodeController = Depends(get_passage_node_controller),
        _=Depends(require_admin),
):
    await controller.delete_node(node_id)


@router.get("/passage/{passage_id}", response_model=Optional[BossNodeRead], description="Get passage boss node")
async def get_boss(
        passage_id: int,
        controller: PassageNodeController = Depends(get_passage_node_controller),
        _=Depends(require_admin),
):
    return await controller.get_boss(passage_id)
