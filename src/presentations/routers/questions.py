from typing import List

from fastapi import APIRouter, Depends

from src.controllers.questions import QuestionController
from src.presentations.depends import (
    get_question_controller,
    require_admin,
)
from src.presentations.schemas.questions import (
    QuestionCreate,
    QuestionRead,
    QuestionUpdate,
)

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.get("/node/{node_id}", response_model=List[QuestionRead])
async def get_questions_by_node(
        node_id: int,
        controller: QuestionController = Depends(get_question_controller),
        _=Depends(require_admin),
):
    return await controller.get_by_node_id(node_id)


@router.post("/node/{node_id}", response_model=QuestionRead)
async def create_question(
        node_id: int,
        body: QuestionCreate,
        controller: QuestionController = Depends(get_question_controller),
        _=Depends(require_admin),
):
    return await controller.create(node_id, body)


@router.patch("/{question_id}", response_model=QuestionRead)
async def update_question(
        question_id: int,
        body: QuestionUpdate,
        controller: QuestionController = Depends(get_question_controller),
        _=Depends(require_admin),
):
    return await controller.update(question_id, body)


@router.delete("/{question_id}")
async def delete_question(
        question_id: int,
        controller: QuestionController = Depends(get_question_controller),
        _=Depends(require_admin),
):
    await controller.delete(question_id)
    return {"message": "Question deleted successfully"}
