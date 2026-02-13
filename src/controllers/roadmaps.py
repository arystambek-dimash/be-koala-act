import json
from typing import Any, Dict, List

from pydantic import BaseModel, Field, ValidationError

from src.app.constants import PROMPTS, QuestionType
from src.app.errors import NotFoundException, InternalServerException
from src.app.openai_service import OpenAIService
from src.app.uow import UoW
from src.presentations.schemas.nodes import NodeDetailedRead
from src.presentations.schemas.questions import (
    QuestionRead,
)
from src.repositories import (
    PassageNodeRepository,
    QuestionRepository,
    PassageRepository,
    UserNodeProgressRepository,
    UserVillageRepository,
)


class GeneratedQuestion(BaseModel):
    type: QuestionType
    text: str
    content: Dict[str, Any] = Field(
        ...,
        description="Question content object with structure depending on question type"
    )


class ListNodeRelationsResponse(BaseModel):
    questions: List[GeneratedQuestion] = Field(
        ...,
        description="List of generated questions for the lesson node"
    )


def parse_ai_response(raw_response: str) -> ListNodeRelationsResponse:
    content = raw_response.strip()

    if content.startswith("```"):
        lines = content.split("\n")
        lines = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
        content = "\n".join(lines)

    try:
        data = json.loads(content)
        return ListNodeRelationsResponse.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as e:
        raise ValueError(f"Failed to parse AI response: {e}")


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
        try:
            db_node = await self.node_repository.get_by_id(node_id)
            if not db_node:
                raise NotFoundException("Node not found")

            passage = await self.passage_repository.get_by_id(db_node.passage_id)
            if not passage:
                raise NotFoundException("Passage not found")

            if not db_node.questions:
                system_prompt = PROMPTS.get(passage.village.subject.value if passage.village else "english")
                user_prompt = f"""
                                GENERATE LESSON CONTENT:
                                - **Title:** {db_node.title}
                                - **Node Content:** {db_node.content or "General vocabulary"}
                                - **Subject:** {passage.village.subject.value if passage.village else "english"}
                                - **Passage:** {passage.title}
                                """

                try:
                    json_instruction = """
                    IMPORTANT: Return ONLY valid JSON in this exact format:
                    {
                        "questions": [
                            {
                                "type": "<question_type>",
                                "text": "<question text>",
                                "content": { <question-specific content> }
                            }
                        ]
                    }
                    Generate 3-5 questions. No markdown, no explanations, just pure JSON.
                    """
                    raw_response = await self.openai_service.request_raw(
                        messages=[
                            {
                                "role": "system",
                                "content": system_prompt + json_instruction,
                            },
                            {
                                "role": "user",
                                "content": user_prompt,
                            }
                        ]
                    )
                    response_json = parse_ai_response(raw_response)
                except Exception as e:
                    print(e)
                    raise InternalServerException("Ai response error")
                print(response_json)
                async with self.uow:
                    generated_questions = []
                    for q in response_json.questions:
                        mutable_dict = q.model_dump()
                        mutable_dict["node_id"] = node_id
                        mutable_dict["content"] = q.content
                        print(mutable_dict)
                        try:
                            generated_questions.append(await self.question_repository.create(**mutable_dict))
                        except Exception as e:
                            print(e)
                            raise InternalServerException("Ai response error")
                db_node.questions = generated_questions
            pydantic_model = NodeDetailedRead.model_validate(db_node)
            pydantic_model.questions = [QuestionRead.model_validate(question) for question in db_node.questions]
            return pydantic_model
        except Exception as e:
            print(e)
            raise e

    async def get_roadmap(self, subject: str, user_id: int):
        user_villages = await self.village_repository.get_user_villages(user_id)
        village_id = None
        for v in user_villages:
            if v.get("village_subject") and v["village_subject"].value == subject:
                village_id = v.get("village_id")
                break

        if not village_id:
            raise NotFoundException(f"No village found for subject: {subject}")

        return await self.passage_repository.get_roadmap(user_id, village_id)
