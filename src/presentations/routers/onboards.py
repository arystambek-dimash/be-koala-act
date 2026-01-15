from fastapi import APIRouter, Depends

from src.controllers.onboards import OnboardController
from src.controllers.subject_onboard import SubjectOnboardController
from src.presentations.depends import (
    get_current_user,
    get_onboard_controller,
    get_subject_onboard_controller,
)
from src.presentations.schemas.onboards import (
    OnboardCreate,
    SingleSubjectOnboard,
)

router = APIRouter(prefix="/onboards", tags=["Onboards"])


@router.post("/user/acquaintance")
async def user_acquaintance(
        data: OnboardCreate,
        onboard_controller: OnboardController = Depends(get_onboard_controller),
        current_user=Depends(get_current_user),
):
    return await onboard_controller.execute(current_user, data)


@router.post("/subject")
async def subject_onboard(
        data: SingleSubjectOnboard,
        controller: SubjectOnboardController = Depends(get_subject_onboard_controller),
        current_user=Depends(get_current_user),
):
    return await controller.execute(current_user, data)
