from fastapi import APIRouter, Depends, Query

from src.controllers.roadmaps import RoadmapController
from src.presentations.depends import get_current_user, get_roadmap_controller
from src.presentations.schemas.nodes import NodeDetailedRead

router = APIRouter(prefix="/roadmaps", tags=["Roadmaps"])


@router.get("/{subject}")
async def get_roadmap(
        subject: str,
        limit: int = Query(default=5, ge=1, le=20),
        controller: RoadmapController = Depends(get_roadmap_controller),
        current_user=Depends(get_current_user),
):
    return await controller.get_roadmap(
        subject=subject,
        user_id=current_user.id,
        limit=limit,
    )


@router.get("/nodes/{node_id}", response_model=NodeDetailedRead)
async def get_node(
        node_id: int,
        controller: RoadmapController = Depends(get_roadmap_controller),
        current_user=Depends(get_current_user),
):
    return await controller.get_node(node_id=node_id)
