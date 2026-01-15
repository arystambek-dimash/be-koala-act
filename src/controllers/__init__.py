from src.controllers.auths import AuthController
from src.controllers.building_progression import BuildingProgressionController
from src.controllers.buildings import BuildingController
from src.controllers.building_collector import BuildingCollectorController
from src.controllers.onboards import OnboardController
from src.controllers.passages import PassageController
from src.controllers.questions import QuestionController
from src.controllers.subject_onboard import SubjectOnboardController
from src.controllers.users import UserController

__all__ = [
    "AuthController",
    "BuildingController",
    "BuildingProgressionController",
    "OnboardController",
    "PassageController",
    "QuestionController",
    "SubjectOnboardController",
    "UserController",
    "BuildingCollectorController"
]
