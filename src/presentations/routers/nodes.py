from typing import List

from fastapi import APIRouter, Depends

from src.controllers.passage_nodes import PassageNodeController
from src.presentations.depends import (
    get_passage_node_controller, require_admin,
)
from src.presentations.schemas.nodes import (
    PassageNodeCreate,
    PassageNodeUpdate,
    NodeRead,
)

router = APIRouter(prefix="/nodes", tags=["Passage Nodes"])


@router.get("/passage/{passage_id}", response_model=List[NodeRead], description="Get passage boss nodes")
async def list_nodes_by_passage(
        passage_id: int,
        controller: PassageNodeController = Depends(get_passage_node_controller),
        _=Depends(require_admin),
):
    return await controller.get_nodes_by_passage(passage_id)


@router.post("/passage/{passage_id}", response_model=NodeRead)
async def create_node(
        passage_id: int,
        body: PassageNodeCreate,
        controller: PassageNodeController = Depends(get_passage_node_controller),
        _=Depends(require_admin),
):
    return await controller.create_node(passage_id, body)


@router.patch("/{node_id}", response_model=NodeRead)
async def update_node(
        node_id: int,
        body: PassageNodeUpdate,
        controller: PassageNodeController = Depends(get_passage_node_controller),
        _=Depends(require_admin),
):
    return await controller.update_node(node_id, body)


@router.delete("/{node_id}")
async def delete_node(
        node_id: int,
        controller: PassageNodeController = Depends(get_passage_node_controller),
        _=Depends(require_admin),
):
    await controller.delete_node(node_id)
