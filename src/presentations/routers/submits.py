from fastapi import APIRouter, Depends

from src.controllers.submits import SubmitController
from src.presentations.depends import get_current_user, get_submit_controller
from src.presentations.schemas.submits import SubmitResponse, SubmitModel

router = APIRouter(prefix="/submits", tags=["Submits"])


@router.post("", response_model=SubmitResponse)
async def submit_node(
        data: SubmitModel,
        controller: SubmitController = Depends(get_submit_controller),
        current_user=Depends(get_current_user)
):
    return await controller.submit(data, current_user.id)
