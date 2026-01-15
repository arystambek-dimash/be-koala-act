import json
from typing import List

from src.app.constants import PROMPTS
from src.app.errors import NotFoundException, InternalServerException
from src.app.openai_service import OpenAIService
from src.app.uow import UoW
from src.presentations.schemas.questions import (
    AIFeedbackRequest,
    AIFeedbackResponse,
    ListNodeRelationsResponse,
    NodeDetailedRead,
    NodeProgressCreate,
    NodeProgressRead,
    QuestionRead,
    WrongQuestionFeedback,
)
from src.repositories import (
    PassageNodeRepository,
    QuestionRepository,
    PassageRepository,
    UserNodeProgressRepository,
    UserVillageRepository,
)


class RoadmapController:
    def __init__(
            self,
            uow: UoW,
            passage_repository: PassageRepository,
            node_repository: PassageNodeRepository,
            village_repository: UserVillageRepository,
            question_repository: QuestionRepository,
            progress_repository: UserNodeProgressRepository,
            openai_service: OpenAIService,
    ):
        self.uow = uow
        self.passage_repository = passage_repository
        self.node_repository = node_repository
        self.village_repository = village_repository
        self.question_repository = question_repository
        self.progress_repository = progress_repository
        self.openai_service = openai_service

    async def get_node(self, node_id: int):
        db_node = await self.node_repository.get_by_id_with_passage(node_id)
        if not db_node:
            raise NotFoundException("Node not found")
        if bool(db_node.questions) is False:
            system_prompt = PROMPTS.get(db_node.passage.subject)
            user_prompt = f"""
                            GENERATE LESSON CONTENT:
                            - **Title:** {db_node.title}
                            - **Node Content:** {db_node.content or "General vocabulary"}
                            - **Subject:** {db_node.passage.subject}
                            - **Passage:** {db_node.passage.title}
                            """

            try:
                response_json: ListNodeRelationsResponse = await self.openai_service.request(
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt,
                        },
                        {
                            "role": "user",
                            "content": json.dumps(user_prompt, ensure_ascii=False),
                        }
                    ],
                    response_format=ListNodeRelationsResponse
                )
            except Exception as e:
                raise InternalServerException("Ai response error")

            async with self.uow:
                generated_questions = []
                for q in response_json.questions:
                    mutable_dict = q.dict()
                    mutable_dict["node_id"] = node_id
                    mutable_dict["content"] = q.content
                    try:
                        generated_questions.append(await self.question_repository.create(**mutable_dict))
                    except Exception as e:
                        raise InternalServerException("Ai response error")
            db_node.questions = generated_questions
        pydantic_model = NodeDetailedRead.model_validate(db_node)
        pydantic_model.questions = [QuestionRead.model_validate(question) for question in db_node.questions]
        return pydantic_model

    async def get_roadmap(self, village_id: int, user_id: int, limit: int = 5):
        user_village = await self.village_repository.get_by_user_and_village(
            user_id=user_id,
            village_id=village_id,
            with_details=True
        )
        user_current_passage = await  self.passage_repository.user_current_passage(
            user_id=user_id,
            village_id=village_id
        )
        if user_village is None:
            raise NotFoundException("User village not found")

        passages = await self.passage_repository.get_user_roadmap(
            user_id=user_id,
            village_id=user_village.village_id,
            passage_id=user_current_passage.id if user_current_passage else None,
            limit=limit,
        )

        result: list[dict] = []

        for passage in passages:
            nodes: list[dict] = []
            prev_completed = True
            completed_count = 0

            for i, node in enumerate(passage.nodes):
                is_completed = bool(node.progresses)
                is_unlocked = (i == 0) or prev_completed

                nodes.append(
                    {
                        "id": node.id,
                        "title": node.title,
                        "content": node.content,
                        "order_index": node.order_index,
                        "is_locked": not is_unlocked,
                        "is_completed": is_completed,
                    }
                )

                if is_completed:
                    completed_count += 1

                prev_completed = is_completed

            all_nodes_completed = (completed_count == len(passage.nodes)) if passage.nodes else True
            is_boss_locked = not all_nodes_completed

            boss = passage.boss
            boss_dict = None
            if boss:
                boss_dict = {
                    "id": boss.id,
                    "title": boss.title,
                    "content": boss.content,
                    "config": boss.config,
                    "pass_score": boss.pass_score,
                    "reward_coins": boss.reward_coins,
                    "reward_xp": boss.reward_xp,
                    "is_locked": is_boss_locked,
                }

            result.append(
                {
                    "id": passage.id,
                    "order_index": passage.order_index,
                    "title": passage.title,
                    "nodes": nodes,
                    "boss": boss_dict,
                }
            )

        return result

    async def submit_progress(
            self,
            user_id: int,
            node_id: int,
            data: NodeProgressCreate,
    ) -> NodeProgressRead:
        db_node = await self.node_repository.get_by_id(node_id)
        if not db_node:
            raise NotFoundException("Node not found")

        xp = data.accuracy * 100

        async with self.uow:
            progress = await self.progress_repository.create_progress(
                user_id=user_id,
                node_id=node_id,
                accuracy=data.accuracy,
                correct_answer=data.correct_answer,
                xp=xp,
            )

        return NodeProgressRead.model_validate(progress)

    async def get_attempts(
            self,
            user_id: int,
            node_id: int,
    ) -> List[NodeProgressRead]:
        db_node = await self.node_repository.get_by_id(node_id)
        if not db_node:
            raise NotFoundException("Node not found")

        attempts = await self.progress_repository.get_all_attempts(
            user_id=user_id,
            node_id=node_id,
        )

        return [NodeProgressRead.model_validate(a) for a in attempts]

    async def get_ai_feedback(
            self,
            node_id: int,
            data: AIFeedbackRequest,
    ) -> AIFeedbackResponse:
        db_node = await self.node_repository.get_by_id_with_passage(node_id)
        if not db_node:
            raise NotFoundException("Node not found")

        questions = await self.question_repository.get_by_node_id(node_id)
        if not questions:
            raise NotFoundException("No questions found for this node")

        question_map = {q.id: q for q in questions}

        wrong_questions = []
        correct_count = 0
        total_count = len(data.answers)

        for answer in data.answers:
            q = question_map.get(answer.question_id)
            if not q:
                continue

            is_correct = self._check_answer(q, answer.user_answer)
            if is_correct:
                correct_count += 1
            else:
                wrong_questions.append({
                    "question_id": q.id,
                    "question_text": q.text,
                    "user_answer": answer.user_answer,
                    "correct_answer": self._get_correct_answer(q),
                    "explanation": q.content.get("explanation", ""),
                })

        accuracy = correct_count / total_count if total_count > 0 else 0
        retest_recommended = accuracy < 0.7

        feedback_prompt = f"""
        The student completed a lesson on "{db_node.title}" in {db_node.passage.subject}.
        They got {correct_count}/{total_count} questions correct (accuracy: {accuracy:.1%}).

        Wrong answers:
        {json.dumps(wrong_questions, indent=2, ensure_ascii=False)}

        Please provide:
        1. A brief overall feedback message (2-3 sentences)
        2. 2-3 specific improvement tips based on their mistakes

        Respond in JSON format:
        {{"overall_feedback": "...", "improvement_tips": ["tip1", "tip2", "tip3"]}}
        """

        try:
            ai_response = await self.openai_service.request_raw(
                messages=[
                    {"role": "system", "content": "You are a helpful tutor providing constructive feedback."},
                    {"role": "user", "content": feedback_prompt},
                ]
            )
            feedback_data = json.loads(ai_response)
        except Exception:
            feedback_data = {
                "overall_feedback": f"You scored {accuracy:.0%}. {'Great job!' if accuracy >= 0.7 else 'Keep practicing!'}",
                "improvement_tips": ["Review the explanations for incorrect answers.", "Practice similar problems."],
            }

        return AIFeedbackResponse(
            overall_feedback=feedback_data.get("overall_feedback", ""),
            wrong_questions=[WrongQuestionFeedback(**wq) for wq in wrong_questions],
            accuracy=accuracy,
            retest_recommended=retest_recommended,
            improvement_tips=feedback_data.get("improvement_tips", []),
        )

    def _check_answer(self, question, user_answer) -> bool:
        content = question.content
        q_type = question.type

        if q_type == "multiple_choice":
            correct_option = next(
                (opt["id"] for opt in content.get("options", []) if opt.get("is_correct")),
                None
            )
            return user_answer == correct_option

        elif q_type == "fill_gap":
            correct = content.get("correct_answer", "").strip().lower()
            return str(user_answer).strip().lower() == correct

        elif q_type == "find_error":
            return user_answer == content.get("error_index")

        elif q_type == "ordering":
            return user_answer == content.get("correct_order")

        elif q_type == "matching":
            return user_answer == content.get("pairs")

        elif q_type == "trend_arrow":
            return str(user_answer).lower() == content.get("correct_trend", "").lower()

        elif q_type == "strike_out":
            return set(user_answer) == set(content.get("correct_ids_to_remove", []))

        return False

    def _get_correct_answer(self, question):
        content = question.content
        q_type = question.type

        if q_type == "multiple_choice":
            return next(
                (opt["text"] for opt in content.get("options", []) if opt.get("is_correct")),
                None
            )
        elif q_type == "fill_gap":
            return content.get("correct_answer")
        elif q_type == "find_error":
            return content.get("correct_word")
        elif q_type == "ordering":
            return content.get("correct_order")
        elif q_type == "trend_arrow":
            return content.get("correct_trend")
        elif q_type == "strike_out":
            return content.get("correct_ids_to_remove")

        return content
