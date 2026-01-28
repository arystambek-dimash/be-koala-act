from typing import Sequence

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from src.app.constants import BuildingType, SubjectEnum
from src.models.buildings import Building
from src.models.node_progresses import UserNodeProgress
from src.models.nodes import PassageNode
from src.models.passages import Passage
from src.models.user_villages import UserVillage
from src.repositories.base import BaseRepository
from src.repositories.utils_repositories import UtilsRepository


class PassageRepository(BaseRepository[Passage], UtilsRepository):
    model = Passage

    async def get_by_id(self, id: int) -> Passage | None:
        stmt = select(Passage).where(Passage.id == id).options(selectinload(Passage.boss))
        result = await self._session.execute(stmt)
        passage = result.scalar_one_or_none()
        return passage

    async def village_passages(
            self,
            village_id: int,
    ) -> Sequence[Passage]:
        stmt = (
            select(Passage)
            .where(
                Passage.village_id == village_id
            )
            .order_by(Passage.order_index.asc())
        )
        return (await self._session.execute(stmt)).scalars().all()

    async def get_roadmap(self, user_id, village_id):
        stmt = select(Passage).where(Passage.village_id == village_id).order_by(Passage.order_index)
        passages = (await self._session.execute(stmt)).scalars().all()
        progress_stmt = select(UserNodeProgress).where(UserNodeProgress.user_id == user_id)
        user_progress_list = (await self._session.execute(progress_stmt)).scalars().all()
        completed_node_ids = {p.node_id for p in user_progress_list if p.correct_answer > 0 or p.accuracy >= 0}
        response_passages = []
        is_passage_unlocked = True
        for passage in passages:
            passage_status = "locked"
            if is_passage_unlocked:
                passage_status = "available"
            passage_data = {
                "id": passage.id,
                "title": passage.title,
                "order_index": passage.order_index,
                "status": passage_status,
                "nodes": [],
                "boss": None
            }

            sorted_nodes = sorted(passage.nodes, key=lambda x: x.id)
            is_node_unlocked = True if passage_status != "locked" else False
            completed_nodes_count = 0

            for node in sorted_nodes:
                is_completed = node.id in completed_node_ids

                node_dto = {
                    "id": node.id,
                    "title": node.title,
                    "content": node.content,
                    "is_completed": is_completed,
                    "is_locked": not is_node_unlocked,
                    "is_current": False
                }
                if not node_dto["is_locked"] and not is_completed:
                    node_dto["is_current"] = True

                passage_data["nodes"].append(node_dto)

                if is_completed:
                    completed_nodes_count += 1
                else:
                    is_node_unlocked = False

            all_nodes_finished = (completed_nodes_count == len(passage_data["nodes"]))
            is_boss_unlocked = (passage_status != "locked") and all_nodes_finished

            boss_completed = False

            if passage.boss:
                boss_completed = passage.boss.id in completed_node_ids

                boss_dto = {
                    "id": passage.boss.id,
                    "title": passage.boss.title,
                    "content": passage.boss.content,
                    "config": passage.boss.config,
                    "is_completed": boss_completed,
                    "is_locked": not is_boss_unlocked,
                    "pass_score": passage.boss.pass_score,
                    "reward_coins": passage.boss.reward_coins,
                }
                passage_data["boss"] = boss_dto
            if passage.boss:
                if boss_completed:
                    passage_data["status"] = "completed"
                    is_passage_unlocked = True
                else:
                    is_passage_unlocked = False
            else:
                if all_nodes_finished:
                    passage_data["status"] = "completed"
                    is_passage_unlocked = True
                else:
                    is_passage_unlocked = False
            if passage_data["status"] == "locked":
                is_passage_unlocked = False

            response_passages.append(passage_data)

        return response_passages

    async def get_next_passages(
            self,
            user_id: int,
            subject: SubjectEnum
    ):
        user_current_village_id = await self._session.scalar(
            select(UserVillage.village_id)
            .join(Building, Building.id == UserVillage.village_id)
            .where(
                UserVillage.user_id == user_id,
                Building.type == BuildingType.VILLAGE,
                Building.subject == subject,
            )
        )
        if user_current_village_id is None:
            user_current_village_id = await self._session.scalar(
                select(Building.id)
                .where(
                    Building.type == BuildingType.VILLAGE,
                    Building.subject == subject,
                )
                .order_by(Building.id.asc())
                .limit(1)
            )
        user_current_passage_id = await self._session.scalar(
            select(func.max(PassageNode.passage_id))
            .where(PassageNode.user_id == user_id)
            .join(
                Passage,
                Passage.village_id == user_current_village_id,
            )
        )

        if not user_current_passage_id:
            stmt = (
                select(Passage)
                .where(Passage.village_id == user_current_village_id)
                .order_by(Passage.order_index.asc())
            )

        else:
            stmt = (
                select(Passage)
                .where(
                    Passage.id > user_current_passage_id
                )
                .order_by(Passage.order_index.asc())
            )
        result = await self._session.execute(stmt)
        passages = result.scalars().all()
        return passages
