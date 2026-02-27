from src.app.constants import FundType
from src.app.errors import NotFoundException
from src.app.uow import UoW
from src.presentations.schemas.questions import (
    MultipleChoiceContent, FindErrorContent, StrikeOutContent,
    OrderingContent, HighlightContent, SwipeDecisionContent, FillGapContent,
    TrendArrowContent, SliderValueContent, MatchingContent, GraphPointContent
)
from src.presentations.schemas.submits import SubmitModel, SubmitResponse
from src.repositories import (
    UserNodeProgressRepository, PassageNodeRepository, QuestionRepository,
    WalletRepository, ExperienceRepository
)

# Награды за обычную ноду
DEFAULT_XP_REWARD = 10
DEFAULT_COINS_REWARD = 5


class SubmitController:
    def __init__(
            self,
            uow: UoW,
            node_repository: PassageNodeRepository,
            user_progress_repository: UserNodeProgressRepository,
            question_repository: QuestionRepository,
            wallet_repository: WalletRepository,
            experience_repository: ExperienceRepository,
    ):
        self.uow = uow
        self.node_repository = node_repository
        self.user_progress_repository = user_progress_repository
        self.question_repository = question_repository
        self.wallet_repository = wallet_repository
        self.experience_repository = experience_repository

    async def submit(self, data: SubmitModel, user_id: int) -> SubmitResponse:
        db_node = await self.node_repository.get_by_id(data.node_id)
        if not db_node:
            raise NotFoundException("Node is not found")

        # Проверяем ответы
        total_points: float = 0.0
        total_questions = len(data.questions)

        for question in data.questions:
            db_question = await self.question_repository.get_by_id(question.question_id)
            if not db_question:
                continue

            total_points += self._check_answer(
                question.content,
                db_question.content,
                question.question_type
            )

        accuracy = total_points / total_questions if total_questions > 0 else 0.0
        correct_answers = int(total_points)

        # Проверяем был ли уже прогресс по этой ноде
        existing_progress = await self.user_progress_repository.get_by_user_and_node(
            user_id,
            node_id=db_node.id,
        )

        # Определяем награды
        xp_reward = db_node.reward_xp if db_node.is_boss and db_node.reward_xp else DEFAULT_XP_REWARD
        coins_reward = db_node.reward_coins if db_node.is_boss and db_node.reward_coins else DEFAULT_COINS_REWARD

        # Первое прохождение - начисляем награды
        is_first_completion = existing_progress is None
        earned_xp = 0
        earned_coins = 0

        async with self.uow:
            if is_first_completion:
                # Создаем прогресс
                await self.user_progress_repository.create(
                    node_id=data.node_id,
                    user_id=user_id,
                    accuracy=accuracy,
                    xp=xp_reward,
                    correct_answer=correct_answers
                )

                # Начисляем XP
                await self.experience_repository.add_xp(user_id, xp_reward)
                earned_xp = xp_reward

                # Начисляем монеты
                await self.wallet_repository.add_funds(
                    user_id=user_id,
                    amount=coins_reward,
                    fund_type=FundType.COIN
                )
                earned_coins = coins_reward

        # Определяем следующую ноду
        next_node_id = await self._get_next_node_id(db_node, user_id)
        next_node_unlocked = next_node_id is not None

        return SubmitResponse(
            earned_xp=earned_xp,
            earned_coins=earned_coins,
            accuracy=accuracy,
            correct_answers=correct_answers,
            total_questions=total_questions,
            is_completed=True,
            next_node_unlocked=next_node_unlocked,
            next_node_id=next_node_id
        )

    async def _get_next_node_id(self, current_node, user_id: int) -> int | None:
        """Находит ID следующей ноды в том же passage."""
        from sqlalchemy import select
        from src.models.nodes import PassageNode

        # Получаем все ноды того же passage
        stmt = (
            select(PassageNode)
            .where(
                PassageNode.passage_id == current_node.passage_id,
                PassageNode.id > current_node.id,
                PassageNode.is_boss == False,
                PassageNode.user_id == None  # только общие ноды
            )
            .order_by(PassageNode.id.asc())
            .limit(1)
        )
        result = await self.node_repository._session.execute(stmt)
        next_node = result.scalar_one_or_none()

        if next_node:
            return next_node.id

        # Если обычных нод нет, проверяем босса
        boss_stmt = (
            select(PassageNode)
            .where(
                PassageNode.passage_id == current_node.passage_id,
                PassageNode.is_boss == True,
                PassageNode.user_id == None
            )
            .limit(1)
        )
        boss_result = await self.node_repository._session.execute(boss_stmt)
        boss_node = boss_result.scalar_one_or_none()

        if boss_node and boss_node.id != current_node.id:
            return boss_node.id

        return None

    def _check_answer(self, user_answer, question_content: dict, question_type: str) -> float:
        """Проверяет ответ пользователя и возвращает балл (0.0 - 1.0)."""
        answer_point: float = 0.0

        if question_type == "multiple_choice":
            multiple_choice = MultipleChoiceContent(**question_content)
            selected_ids = {o.id for o in user_answer.options}
            correct_ids = {o.id for o in multiple_choice.options if o.is_correct}

            if not correct_ids:
                return 0.0

            picked_correct = len(correct_ids & selected_ids)
            answer_point = picked_correct / len(correct_ids)

        elif question_type == "find_error":
            find_error = FindErrorContent(**question_content)
            answer_point = 1.0 if find_error.error_index == user_answer.error_index else 0.0

        elif question_type == "strike_out":
            strike_out = StrikeOutContent(**question_content)
            correct = set(strike_out.correct_ids_to_remove)
            chosen = set(user_answer.removed_ids)
            if correct:
                answer_point = len(correct & chosen) / len(correct)

        elif question_type == "ordering":
            ordering = OrderingContent(**question_content)
            answer_point = 1.0 if user_answer.ordered_items == ordering.correct_order else 0.0

        elif question_type == "highlight":
            highlight = HighlightContent(**question_content)
            answer_point = 1.0 if user_answer.selected_phrase == highlight.correct_phrase else 0.0

        elif question_type == "swipe_decision":
            swipe_decision = SwipeDecisionContent(**question_content)
            answer_point = 1.0 if user_answer.swipe == swipe_decision.correct_swipe else 0.0

        elif question_type == "fill_gap":
            fill_gap = FillGapContent(**question_content)
            # Case-insensitive сравнение для текстовых ответов
            user_ans = str(user_answer.answer).strip().lower()
            correct_ans = str(fill_gap.correct_answer).strip().lower()
            answer_point = 1.0 if user_ans == correct_ans else 0.0

        elif question_type == "matching":
            matching = MatchingContent(**question_content)
            # Новый формат: сравниваем пары по ID
            user_pairs = {(p.left_id, p.right_id) for p in user_answer.pairs}
            correct_pairs = {(p.left_id, p.right_id) for p in matching.correct_pairs}

            if not correct_pairs:
                answer_point = 0.0
            else:
                answer_point = len(user_pairs & correct_pairs) / len(correct_pairs)

        elif question_type == "graph_point":
            graph_point = GraphPointContent(**question_content)
            dx = float(user_answer.x) - float(graph_point.target_x)
            dy = float(user_answer.y) - float(graph_point.target_y)
            r = float(graph_point.radius)
            answer_point = 1.0 if (dx * dx + dy * dy) <= (r * r) else 0.0

        elif question_type == "trend_arrow":
            trend_arrow = TrendArrowContent(**question_content)
            answer_point = 1.0 if user_answer.trend == trend_arrow.correct_trend else 0.0

        elif question_type == "slider_value":
            slider_value = SliderValueContent(**question_content)
            # Проверяем с учетом tolerance
            diff = abs(float(user_answer.value) - float(slider_value.correct_value))
            answer_point = 1.0 if diff <= slider_value.tolerance else 0.0

        return answer_point
