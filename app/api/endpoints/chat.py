from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse, Source
from app.services.chatbot import Chatbot
from app.db.vectorstore import VectorStoreHandler

router = APIRouter(prefix="/chat", tags=["chat"])
_bot = Chatbot()
_vs = _bot.pipeline.vectorstore  # 이미 로드된 핸들러 재사용

@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        docs = _vs.search(req.question, top_k=req.top_k)
        answer = _bot.chat(req.question)

        sources = [
            Source(
                text=d.page_content[:500],
                metadata=getattr(d, "metadata", None)
            )
            for d in docs
        ]
        return ChatResponse(answer=answer, sources=sources)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error")
