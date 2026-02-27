"""
DEV-only endpoints for local development and testing.
All endpoints here only work when DEBUG=True.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette.requests import Request

from src.app.constants import SubjectEnum, BuildingType, FundType
from src.app.uow import UoW
from src.presentations.depends import (
    get_current_user,
    get_uow,
    get_building_repository,
    get_user_castle_repository,
    get_user_village_repository,
    get_experience_repository,
    get_user_repository,
)
from src.repositories import (
    BuildingRepository,
    UserCastleRepository,
    UserVillageRepository,
    ExperienceRepository,
    UserRepository,
)

router = APIRouter(prefix="/dev", tags=["Dev (DEBUG only)"])


class SeedDataResponse(BaseModel):
    message: str
    castle_id: int | None
    villages: list[dict]


@router.post("/seed-data", response_model=SeedDataResponse)
async def seed_user_data(
        request: Request,
        uow: UoW = Depends(get_uow),
        building_repo: BuildingRepository = Depends(get_building_repository),
        castle_repo: UserCastleRepository = Depends(get_user_castle_repository),
        village_repo: UserVillageRepository = Depends(get_user_village_repository),
        experience_repo: ExperienceRepository = Depends(get_experience_repository),
        current_user=Depends(get_current_user),
):
    """
    DEV ONLY: Create Castle + Villages + Experience for current user.
    Only works when DEBUG=True.
    """
    settings = request.app.state.settings

    if not settings.DEBUG:
        raise HTTPException(status_code=404, detail="Not found")

    user_id = current_user.id
    created_villages = []

    async with uow:
        # 1. Check/Create Experience
        existing_exp = await experience_repo.get_by_user_id(user_id)
        if not existing_exp:
            await experience_repo.create(
                user_id=user_id,
                level=1,
                current_xp=0,
            )

        # 2. Check/Create Castle
        existing_castle = await castle_repo.get_user_castle(user_id)
        castle_id = None

        if not existing_castle:
            # Get first castle template
            first_castle = await building_repo.get_user_next_castle(user_id)
            if first_castle:
                await castle_repo.create(
                    user_id=user_id,
                    castle_id=first_castle.id,
                )
                castle_id = first_castle.id
        else:
            castle_id = existing_castle.get("castle_id")

        # 3. Check/Create Villages for all subjects
        for subject in SubjectEnum:
            # Check if village exists for this subject
            existing_villages = await village_repo.get_user_villages(user_id)
            has_subject = any(
                v.get("village_subject") == subject
                for v in existing_villages
            )

            if not has_subject:
                # Get first village for this subject
                first_village = await building_repo.get_user_next_village(user_id, subject)
                if first_village:
                    await village_repo.create(
                        user_id=user_id,
                        village_id=first_village.id,
                    )
                    created_villages.append({
                        "subject": subject.value,
                        "village_id": first_village.id,
                        "status": "created"
                    })
                else:
                    created_villages.append({
                        "subject": subject.value,
                        "village_id": None,
                        "status": "no_template_found"
                    })
            else:
                village_id = next(
                    (v.get("village_id") for v in existing_villages if v.get("village_subject") == subject),
                    None
                )
                created_villages.append({
                    "subject": subject.value,
                    "village_id": village_id,
                    "status": "already_exists"
                })

    return SeedDataResponse(
        message="Seed data created successfully",
        castle_id=castle_id,
        villages=created_villages,
    )


@router.get("/check")
async def dev_check(request: Request):
    """Check if dev mode is enabled."""
    settings = request.app.state.settings
    return {
        "debug": settings.DEBUG,
        "dev_endpoints_available": settings.DEBUG,
    }


@router.get("/my-progress")
async def get_my_progress(
        request: Request,
        uow: UoW = Depends(get_uow),
        current_user=Depends(get_current_user),
):
    """
    DEV ONLY: Check user's progress, experience, wallet.
    """
    settings = request.app.state.settings
    if not settings.DEBUG:
        raise HTTPException(status_code=404, detail="Not found")

    from sqlalchemy import select
    from src.models.node_progresses import UserNodeProgress
    from src.models.experiences import Experience
    from src.models.wallets import Wallet

    session = uow._session
    user_id = current_user.id

    # Get progress
    progress_result = await session.execute(
        select(UserNodeProgress).where(UserNodeProgress.user_id == user_id)
    )
    progresses = progress_result.scalars().all()

    # Get experience
    exp_result = await session.execute(
        select(Experience).where(Experience.user_id == user_id).limit(1)
    )
    experience = exp_result.scalar_one_or_none()

    # Get wallet
    wallet_result = await session.execute(
        select(Wallet).where(Wallet.user_id == user_id)
    )
    wallets = wallet_result.scalars().all()

    return {
        "user_id": user_id,
        "experience": {
            "level": experience.level if experience else None,
            "current_xp": experience.current_xp if experience else None,
        } if experience else None,
        "wallets": [
            {"fund_type": w.fund_type.value, "fund": w.fund}
            for w in wallets
        ],
        "completed_nodes": [
            {
                "node_id": p.node_id,
                "accuracy": p.accuracy,
                "xp": p.xp,
                "correct_answer": p.correct_answer,
            }
            for p in progresses
        ],
        "total_completed": len(progresses),
    }


@router.delete("/clear-questions")
async def clear_all_questions(
        request: Request,
        uow: UoW = Depends(get_uow),
        current_user=Depends(get_current_user),
):
    """
    DEV ONLY: Delete all questions so they regenerate with new format.
    """
    settings = request.app.state.settings
    if not settings.DEBUG:
        raise HTTPException(status_code=404, detail="Not found")

    from sqlalchemy import delete
    from src.models.questions import Question

    async with uow:
        # Get session from uow
        session = uow._session
        result = await session.execute(delete(Question))
        deleted_count = result.rowcount

    return {
        "message": f"Deleted {deleted_count} questions. They will regenerate on next node access.",
        "deleted_count": deleted_count,
    }


@router.post("/reset-onboard")
async def reset_onboard(
        request: Request,
        uow: UoW = Depends(get_uow),
        user_repo: UserRepository = Depends(get_user_repository),
        current_user=Depends(get_current_user),
):
    """
    DEV ONLY: Reset has_onboard to false for current user.
    Use this to test onboarding flow again.
    """
    settings = request.app.state.settings
    if not settings.DEBUG:
        raise HTTPException(status_code=404, detail="Not found")

    async with uow:
        await user_repo.update(current_user.id, has_onboard=False)

    return {
        "message": "Onboard reset successfully",
        "user_id": current_user.id,
        "has_onboard": False,
    }


@router.delete("/cleanup-duplicates")
async def cleanup_duplicate_experiences(
        request: Request,
        uow: UoW = Depends(get_uow),
        current_user=Depends(get_current_user),
):
    """
    DEV ONLY: Remove duplicate Experience records for current user.
    Keeps only the first record.
    """
    settings = request.app.state.settings
    if not settings.DEBUG:
        raise HTTPException(status_code=404, detail="Not found")

    from sqlalchemy import select, delete, func
    from src.models.experiences import Experience

    async with uow:
        session = uow._session

        # Find all experience records for this user
        result = await session.execute(
            select(Experience)
            .where(Experience.user_id == current_user.id)
            .order_by(Experience.id)
        )
        experiences = result.scalars().all()

        deleted_count = 0
        if len(experiences) > 1:
            # Keep first, delete rest
            ids_to_delete = [exp.id for exp in experiences[1:]]
            await session.execute(
                delete(Experience).where(Experience.id.in_(ids_to_delete))
            )
            deleted_count = len(ids_to_delete)

    return {
        "message": f"Cleaned up {deleted_count} duplicate experience records",
        "deleted_count": deleted_count,
        "kept_experience_id": experiences[0].id if experiences else None,
    }


@router.get("/db-check")
async def check_database_state(
        request: Request,
        uow: UoW = Depends(get_uow),
):
    """
    DEV ONLY: Check database state - buildings, passages, etc.
    No auth required for quick debugging.
    """
    settings = request.app.state.settings
    if not settings.DEBUG:
        raise HTTPException(status_code=404, detail="Not found")

    from sqlalchemy import select, func
    from src.models.buildings import Building
    from src.models.passages import Passage

    session = uow._session

    # Count castles
    castles = await session.execute(
        select(Building.id, Building.title)
        .where(Building.type == BuildingType.CASTLE)
        .order_by(Building.id)
    )
    castle_list = [{"id": r[0], "title": r[1]} for r in castles.all()]

    # Count villages by subject
    villages = await session.execute(
        select(Building.id, Building.title, Building.subject)
        .where(Building.type == BuildingType.VILLAGE)
        .order_by(Building.subject, Building.id)
    )
    village_list = [{"id": r[0], "title": r[1], "subject": r[2].value if r[2] else None} for r in villages.all()]

    # Get all passages with subject
    passages = await session.execute(
        select(Passage.id, Passage.title, Building.subject)
        .join(Building, Building.id == Passage.village_id)
        .where(Building.subject.isnot(None))
        .order_by(Building.subject, Passage.id)
    )
    passage_list = [{"id": r[0], "title": r[1], "subject": r[2].value} for r in passages.all()]

    return {
        "castles": castle_list,
        "castles_count": len(castle_list),
        "villages": village_list,
        "villages_count": len(village_list),
        "passages": passage_list,
        "passages_count": len(passage_list),
        "status": "ok" if castle_list else "NO CASTLES - need to create castle building first!",
    }
