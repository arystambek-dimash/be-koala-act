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

    async def request_raw(
            self,
            messages: List[Dict[str, str]],
            model: str = "gpt-4o-mini",
    ) -> str:
        """Make a raw chat completion request and return the content as string."""
        completion = await self.client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return completion.choices[0].message.content or ""
