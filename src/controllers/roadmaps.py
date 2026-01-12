from src.app.errors import BadRequestException
from src.app.uow import UoW
from src.repositories import PassageNodeRepository, UserVillageRepository, UserNodeProgressRepository, PassageRepository


class RoadmapController:
    def __init__(
            self,
            uow: UoW,
            passage_repository: PassageRepository,
            node_repository: PassageNodeRepository,
            village_repository: UserVillageRepository,
            user_progress_repository: UserNodeProgressRepository
    ):
        self.uow = uow
        self.passage_repository = passage_repository
        self.node_repository = node_repository
        self.village_repository = village_repository
        self.user_progress_repository = user_progress_repository

    async def get_node(self, node_id: int):
        ...

    async def get_roadmap(
            self,
            subject: str,
            user_id: int,
            passage_quantity: int = 5
    ):
        village = await self.village_repository.get_by_user_and_village_subject(
            user_id=user_id,
            subject=subject
        )

        if village is None:
            raise BadRequestException()

        user_current_passage = await self.passage_repository.current_user_passage(
            user_id=user_id,
            subject=subject
        )
