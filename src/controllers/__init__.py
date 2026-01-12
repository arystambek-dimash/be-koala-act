from src.controllers.auths import AuthController
from src.controllers.building_progression import BuildingProgressionController
from src.controllers.buildings import BuildingController
from src.controllers.onboards import OnboardController
from src.controllers.passages import PassageController, PassageBossController
from src.controllers.subject_onboard import SubjectOnboardController
from src.controllers.castle_collector import (
    CastleCollectorController,
    VillageCollectorController,
)
from src.controllers.users import UserController

__all__ = [
    "AuthController",
    "BuildingController",
    "BuildingProgressionController",
    "CastleCollectorController",
    "OnboardController",
    "PassageBossController",
    "PassageController",
    "SubjectOnboardController",
    "UserController",
    "VillageCollectorController",
]
