from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse, Source
from app.services.rag import RAGPipeline
from app.services.storage_utils import signed_url  # ★ 서명 URL 유틸

router = APIRouter(prefix="/chat", tags=["chat"])
_pipeline = RAGPipeline()  # 내부에서 벡터스토어 로드


def _enrich_metadata(md: dict | None, url_ttl_minutes: int = 10) -> dict | None:
    """
    RAGPipeline이 반환한 source의 metadata에 'gs_path'가 있다면
    즉석에서 'source_url'(서명 URL)을 주입해 프론트가 바로 열 수 있도록 보강.
    """
    md = dict(md or {})
    gs_path = md.get("gs_path")
    if gs_path:
        try:
            md["source_url"] = signed_url(gs_path, minutes=url_ttl_minutes, inline=True)
        except Exception:
            # 서명 실패해도 나머지 흐름은 유지
            pass
        if not md.get("title"):
            md["title"] = gs_path.split("/")[-1]
    return md


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    질문 → (RAGPipeline) 답변 + 출처 → 출처 메타데이터에 source_url 주입 → 반환
    RAGPipeline.generate_answer_with_sources()는 (answer, sources) 형태라고 가정.
    sources의 각 항목은 {"text":..., "metadata":{...}, "score":..., "confidence":...} 구조.
    """
    try:
        # 요청 top_k 반영(선택)
        _pipeline.top_k = req.top_k

        answer, srcs = _pipeline.generate_answer_with_sources(req.question)

        sources = [
            Source(
                text=s.get("text", ""),
                score=s.get("score"),
                confidence=s.get("confidence"),
                metadata=_enrich_metadata(s.get("metadata"), url_ttl_minutes=10),
            )
            for s in srcs
        ]
        return ChatResponse(answer=answer, sources=sources)

    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception:
        # 실제 운영 시 로깅 추가 권장
        raise HTTPException(status_code=500, detail="Unexpected error")