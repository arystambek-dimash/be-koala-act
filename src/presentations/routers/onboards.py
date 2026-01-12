from fastapi import APIRouter, Depends

from src.controllers.onboards import OnboardController
from src.controllers.users import UserController
from src.presentations.depends import get_current_user
from src.presentations.schemas.onboards import OnboardCreate
from src.presentations.schemas.users import UserRead

router = APIRouter(prefix="/onboards", tags=["Onboards"])


@router.post("/user/acquaintance")
async def profile_update(
        data: OnboardCreate,
        onboard_controller: OnboardController = Depends(get_current_user),
        current_user: UserRead = Depends(get_current_user),
):
    return await onboard_controller.execute(current_user, data)
