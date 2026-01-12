from src.models.buildings import Building
from src.repositories.base import BaseRepository


class BuildingRepository(BaseRepository[Building]):
    model = Building
