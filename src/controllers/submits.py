from src.app.errors import NotFoundException
from src.app.uow import UoW
from src.presentations.schemas.questions import MultipleChoiceContent, FindErrorContent, StrikeOutContent, \
    OrderingContent, HighlightContent, SwipeDecisionContent, FillGapContent, TrendArrowContent, SliderValueContent, \
    MatchingContent, GraphPointContent
from src.presentations.schemas.submits import SubmitModel, SubmitContentType
from src.repositories import UserNodeProgressRepository, PassageNodeRepository, QuestionRepository


class SubmitController:
    def __init__(
            self,
            uow: UoW,
            node_repository: PassageNodeRepository,
            user_progress_repository: UserNodeProgressRepository,
            question_repository: QuestionRepository,
    ):
        self.uow = uow
        self.node_repository = node_repository
        self.user_progress_repository = user_progress_repository
        self.question_repository = question_repository

    async def submit(self, data: SubmitModel, user_id: int):
        db_node = await self.node_repository.get_by_id(data.node_id)
        if not db_node:
            raise NotFoundException("Node is not found")

        def check_answer(user_answer: SubmitContentType, question_content: dict, question_type: str) -> float:
            answer_point: float = 0.0

            if question_type == "multiple_choice":
                multiple_choice = MultipleChoiceContent(**question_content)
                selected_ids = {o.id for o in user_answer.options}  # важно

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
                answer_point = 1.0 if user_answer.answer == fill_gap.correct_answer else 0.0

            elif question_type == "matching":
                matching = MatchingContent(**question_content)

                user_pairs = {(m.left, m.right) for m in user_answer.matches}
                correct_pairs = {(p.left, p.right) for p in matching.pairs}

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
                answer_point = 1.0 if user_answer.value == slider_value.correct_value else 0.0

            return answer_point

        point: float = 0.0

        for question in data.questions:
            db_question = await self.question_repository.get_by_id(question.question_id)  # важно
            if not db_question:
                continue

            point += check_answer(question.content, db_question.content, question.question_type)

        accuracy = point / len(data.questions) if data.questions else 0.0
        node_user_progress = await self.user_progress_repository.get_by_user_and_node(
            user_id,
            node_id=db_node.id,
        )
        if not node_user_progress:
            node_user_progress = await self.user_progress_repository.create(
                node_id=data.node_id,
                user_id=user_id,
                accuracy=accuracy,
                xp=db_node.reward_xp if db_node.is_boss else 10,
                correct_answer=point
            )
            return {
                "earned_xp": node_user_progress.xp,
                "accuracy": accuracy,
                "correct_answers": point,
            }
        else:
            return {
                "earned_xp": 0,
                "accuracy": accuracy,
                "correct_answers": point,
            }
