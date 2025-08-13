import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

class OpenAIClient:
    def __init__(self, api_key: str = None, model: str = "gpt-4o"): # 성능 개선시 str = "gpt-4o" 로 변경하기
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = OpenAI(api_key=self.api_key)

    def chat(self, messages: list[dict], temperature: float = 0.7, max_tokens: int = 1024) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
