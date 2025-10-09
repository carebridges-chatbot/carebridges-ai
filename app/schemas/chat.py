from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ChatRequest(BaseModel):
    question: str = Field(..., description="사용자 질문")
    top_k: int = Field(5, ge=1, le=20, description="검색할 상위 문서 수")

class Source(BaseModel):
    text: str
    metadata: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source] = []
