from dataclasses import dataclass
from typing import List, Sequence

from pydantic import BaseModel

from src.app.openai_service import OpenAIService
from src.models.nodes import PassageNode
from src.presentations.schemas.onboards import PassageOnboard
from src.repositories import PassageNodeRepository


class NodeModel(BaseModel):
    node_title: str
    node_content: str
    passage_id: int


class NodeAIResponse(BaseModel):
    nodes: List[NodeModel]


NODE_GENERATION_PROMPT = """You are an expert educational content generator specializing in SAT/ACT test preparation.

Your task is to generate a personalized learning roadmap with nodes based on:
1. The user's self-assessed level for each passage/topic
2. The passage IDs provided

For each passage, generate 1-3 nodes depending on user level:
- "weak" or "no_idea": Generate 3 detailed nodes (basics -> intermediate -> practice)
- "know_not_good": Generate 2 nodes (review -> practice)
- "strong": Generate 1 node (advanced practice/tips)

Each node should have:
- A clear, descriptive title
- Comprehensive content explaining the concept
- The passage_id it belongs to

Return nodes in the order they should be studied (easier concepts first, building up complexity).

IMPORTANT: Only use passage_ids that are provided in the input. Do not invent new passage_ids."""


@dataclass
class GenerationResult:
    nodes_created: int
    nodes: Sequence[PassageNode]


class PassageNodeGenerator:
    def __init__(
            self,
            node_repository: PassageNodeRepository,
            openai_service: OpenAIService,
    ):
        self._node_repository = node_repository
        self._openai_service = openai_service

    async def generate(
            self,
            passages: List[PassageOnboard],
            user_id: int | None = None,
    ) -> GenerationResult:
        if not passages:
            return GenerationResult(nodes_created=0, nodes=[])

        response = await self._request_ai_generation(passages)

        if not response.nodes:
            return GenerationResult(nodes_created=0, nodes=[])

        return await self._persist_nodes(response, passages, user_id)

    async def _request_ai_generation(
            self,
            passages: List[PassageOnboard],
    ) -> NodeAIResponse:
        passages_data = [
            {"passage_id": p.passage_id, "user_level": p.user_level.value}
            for p in passages
        ]

        return await self._openai_service.request(
            messages=[
                {"role": "system", "content": NODE_GENERATION_PROMPT},
                {"role": "user", "content": str(passages_data)},
            ],
            response_format=NodeAIResponse,
        )

    async def _persist_nodes(
            self,
            response: NodeAIResponse,
            passages: List[PassageOnboard],
            user_id: int | None = None,
    ) -> GenerationResult:
        valid_passage_ids = {p.passage_id for p in passages}

        nodes_to_create = []
        for node in response.nodes:
            if node.passage_id in valid_passage_ids:
                nodes_to_create.append({
                    "passage_id": node.passage_id,
                    "title": node.node_title,
                    "content": node.node_content,
                    "is_boss": False,
                    "user_id": user_id,
                    "config": {},
                })

        if not nodes_to_create:
            return GenerationResult(nodes_created=0, nodes=[])

        created = await self._node_repository.bulk_create(nodes_to_create)
        return GenerationResult(nodes_created=len(created), nodes=created)
