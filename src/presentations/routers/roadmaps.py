from typing import List

from fastapi import APIRouter, Depends, Query

from src.controllers.roadmaps import RoadmapController
from src.presentations.depends import get_current_user, get_roadmap_controller
from src.presentations.schemas.questions import (
    AIFeedbackRequest,
    AIFeedbackResponse,
    NodeDetailedRead,
    NodeProgressCreate,
    NodeProgressRead,
)

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


@router.post("/nodes/{node_id}/progress", response_model=NodeProgressRead)
async def submit_node_progress(
        node_id: int,
        data: NodeProgressCreate,
        controller: RoadmapController = Depends(get_roadmap_controller),
        current_user=Depends(get_current_user),
):
    """Submit user progress for a node (accuracy, correct answers)."""
    return await controller.submit_progress(
        user_id=current_user.id,
        node_id=node_id,
        data=data,
    )


@router.get("/nodes/{node_id}/attempts", response_model=List[NodeProgressRead])
async def get_node_attempts(
        node_id: int,
        controller: RoadmapController = Depends(get_roadmap_controller),
        current_user=Depends(get_current_user),
):
    """Get all attempts/progress history for a user on a specific node."""
    return await controller.get_attempts(
        user_id=current_user.id,
        node_id=node_id,
    )


@router.post("/nodes/{node_id}/feedback", response_model=AIFeedbackResponse)
async def get_ai_feedback(
        node_id: int,
        data: AIFeedbackRequest,
        controller: RoadmapController = Depends(get_roadmap_controller),
        _=Depends(get_current_user),
):
    """Get AI-generated feedback on user's answers with improvement tips."""
    return await controller.get_ai_feedback(
        node_id=node_id,
        data=data,
    )
