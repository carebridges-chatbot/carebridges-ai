from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from langchain_core.documents import Document

from app.db.vectorstore import VectorStoreHandler
from app.services.storage_utils import signed_url  # v4 Signed URL 유틸

router = APIRouter(prefix="/retriever", tags=["retriever"])


# ---------- Pydantic Schemas ----------
class RetrievalItem(BaseModel):
    text: str
    title: Optional[str] = None
    page: Optional[int] = None
    source_url: Optional[str] = None
    score: Optional[float] = None
    confidence: Optional[float] = None


class RetrievalResponse(BaseModel):
    results: List[RetrievalItem]


# ---------- Retriever Core ----------
class Retriever:
    def __init__(self, persist_path: str = "db/faiss_index", url_ttl_minutes: int = 10):
        """
        벡터스토어 로드 + 서명 URL 유효시간 설정
        """
        self.vs_handler = VectorStoreHandler(persist_path)
        self.vs_handler.load_vectorstore()
        self.url_ttl_minutes = url_ttl_minutes

    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        """
        쿼리를 기반으로 검색하고, 각 문서 메타데이터에 서명 URL(source_url)을 주입.
        VectorStoreHandler.search(...)는 List[Document]를 반환한다고 가정.
        """
        docs = self.vs_handler.search(query=query, top_k=top_k)

        for d in docs:
            md = dict(getattr(d, "metadata", {}) or {})
            gs_path = md.get("gs_path")
            if gs_path:
                try:
                    md["source_url"] = signed_url(gs_path, minutes=self.url_ttl_minutes, inline=True)
                except Exception:
                    # 서명 실패해도 검색 자체는 계속
                    pass
            if gs_path and not md.get("title"):
                md["title"] = gs_path.split("/")[-1]
            d.metadata = md
        return docs

    def retrieve_json(self, query: str, top_k: int = 5) -> List[RetrievalItem]:
        docs = self.retrieve(query, top_k=top_k)
        items: List[RetrievalItem] = []
        for d in docs:
            md = d.metadata or {}
            items.append(
                RetrievalItem(
                    text=d.page_content,
                    title=md.get("title"),
                    page=md.get("page"),
                    source_url=md.get("source_url"),
                    score=md.get("score"),
                    confidence=md.get("confidence"),
                )
            )
        return items


# ---------- FastAPI Endpoints ----------
_retriever = Retriever(persist_path="db/faiss_index", url_ttl_minutes=10)

@router.get("/search", response_model=RetrievalResponse)
def search(q: str = Query(..., description="검색 쿼리"), k: int = Query(5, ge=1, le=50)):
    try:
        results = _retriever.retrieve_json(query=q, top_k=k)
        return RetrievalResponse(results=results)
    except FileNotFoundError as e:
        # 인덱스가 아직 없을 때 등
        raise HTTPException(status_code=503, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected error")
