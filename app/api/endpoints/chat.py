from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse, Source
from app.services.rag import RAGPipeline

router = APIRouter(prefix="/chat", tags=["chat"])
_pipeline = RAGPipeline()  # 내부에서 벡터스토어 로드

@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        # 요청 top_k 반영(선택)
        _pipeline.top_k = req.top_k

        answer, srcs = _pipeline.generate_answer_with_sources(req.question)

        sources = [
            Source(
                text=s["text"],
                score=s.get("score"),
                confidence=s.get("confidence"),
                metadata=s.get("metadata"),
            )
            for s in srcs
        ]
        return ChatResponse(answer=answer, sources=sources)

    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        # 실제 운영 시 로깅 추가 권장
        raise HTTPException(status_code=500, detail="Unexpected error")
