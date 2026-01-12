from fastapi import APIRouter, Depends

from src.controllers.users import UserController
from src.presentations.depends import get_current_user
from src.presentations.schemas.users import UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.patch("/profile")
async def profile_update(
        profile: UserUpdate,
        user_controller: UserController,
        current_user: UserRead = Depends(get_current_user),
):
    return await user_controller.profile_update(current_user.id, profile)


@router.get("/profile", response_model=UserRead)
async def profile_read(
        current_user: UserRead = Depends(get_current_user),
):
    return UserRead.from_orm(current_user)
