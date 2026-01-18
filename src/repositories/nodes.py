from src.models.nodes import PassageNode
from src.repositories.base import BaseRepository


class PassageNodeRepository(BaseRepository[PassageNode]):
    model = PassageNode
