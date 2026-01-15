from fastapi import APIRouter, Depends

from src.controllers.users import UserController
from src.presentations.depends import (
    get_current_user,
    get_user_controller,
)
from src.presentations.schemas.users import (
    UserRead,
    UserUpdate,
    UserCastleWithVillages,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.patch("/profile", response_model=UserRead)
async def profile_update(
        profile: UserUpdate,
        user_controller: UserController = Depends(get_user_controller),
        current_user=Depends(get_current_user),
):
    return await user_controller.profile_update(current_user.id, profile)


@router.get("/profile", response_model=UserRead)
async def profile_read(
        current_user=Depends(get_current_user),
):
    return UserRead.model_validate(current_user)


@router.get("/buildings", response_model=UserCastleWithVillages)
async def get_user_buildings(
        user_controller: UserController = Depends(get_user_controller),
        current_user=Depends(get_current_user),
):
    return await user_controller.get_user_buildings(current_user.id)
