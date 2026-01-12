from typing import List, Dict, Any

from openai import AsyncOpenAI, BaseModel


class OpenAIService:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def request(
            self,
            messages: List[Dict[str, str]],
            response_format: BaseModel,
    ) -> Any:
        completion = await self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=messages,
            response_format=response_format,
        )
        response = completion.choices[0].message.parsed
        return response
