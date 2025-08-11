from pydantic import BaseModel, Field
from typing import List, Optional

class ChatRequest(BaseModel):
    question: str = Field(..., description="사용자 질문")
    top_k: int = Field(5, ge=1, le=20)

class Source(BaseModel):
    text: str
    score: Optional[float] = None
    metadata: Optional[dict] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source] = []
