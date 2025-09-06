# services/rag.py
import os
from typing import List, Tuple, Dict, Any
from langchain_core.documents import Document
from app.db.vectorstore import VectorStoreHandler
from app.services.prompt_builder import build_prompt
from app.services.openai_client import OpenAIClient
from app.services.storage_utils import signed_url   #  추가: 서명 URL 유틸

# ===== 설정 =====
THRESHOLD_DISTANCE = float(os.getenv("THRESHOLD_DISTANCE", "0.32"))  # 작을수록 유사(거리)
MIN_DOCS = int(os.getenv("MIN_DOCS", "1"))                            # 통과 문서 최소 개수
FALLBACK_MSG = os.getenv("FALLBACK_MSG", "사회복지와 관련된 질문만 해주세요.")
SIGNED_URL_TTL_MIN = int(os.getenv("SIGNED_URL_TTL_MIN", "10"))       # ★ 링크 유효시간(분)

# LLM 프롬프트 안전 가드(문자 기준; 필요 시 토큰 기준으로 교체 가능)
MAX_DOC_CHARS_FOR_LLM = int(os.getenv("MAX_DOC_CHARS_FOR_LLM", "1800"))
MAX_CONTEXT_CHARS_BUDGET = int(os.getenv("MAX_CONTEXT_CHARS_BUDGET", "9000"))

SMALLTALK_SET = {
    "안녕", "안녕하세요", "하이", "hi", "hello", "헬로", "테스트", "test",
    "고마워", "감사", "뭐해", "누구야"
}

def is_smalltalk(text: str) -> bool:
    q = text.strip().lower()
    return q in SMALLTALK_SET or len(q) <= 2

def score_to_confidence(score: float) -> float:
    """
    거리(score>=0)를 0~1 확신도로 변환.
    단조 감소 변환: conf = 1 / (1 + score)
    """
    return round(1.0 / (1.0 + max(0.0, float(score))), 3)

class RAGPipeline:
    def __init__(self, top_k: int = 5):
        self.vectorstore = VectorStoreHandler()
        self.vectorstore.load_vectorstore()
        self.prompt_builder = build_prompt
        self.llm = OpenAIClient()
        self.top_k = top_k

    def _retrieve_pairs(self, question: str) -> List[Tuple[Document, float]]:
        return self.vectorstore.search_with_threshold(
            query=question,
            top_k=self.top_k,
            threshold=THRESHOLD_DISTANCE
        )

    # ★ LLM 컨텍스트 초과 방지용 트리머(문자 기준)
    def _trim_docs_for_llm(self, docs: List[Document]) -> List[str]:
        clipped: List[str] = []
        budget = MAX_CONTEXT_CHARS_BUDGET
        for d in docs:
            piece = (d.page_content or "")
            if not piece:
                continue
            # 개별 청크 상한
            piece = piece[:MAX_DOC_CHARS_FOR_LLM]
            # 전체 예산 내로 컷
            if len(piece) > budget:
                piece = piece[:max(0, budget)]
            if not piece:
                break
            clipped.append(piece)
            budget -= len(piece)
            if budget <= 0:
                break
        return clipped

    def generate_answer(self, question: str) -> str:
        # 0) 스몰토크/의미 약한 입력 차단
        if is_smalltalk(question):
            return FALLBACK_MSG

        # 1) 임계값 필터 적용 검색
        pairs = self._retrieve_pairs(question)

        # 2) 최소 문서 수 미만이면 차단
        if len(pairs) < MIN_DOCS:
            return FALLBACK_MSG

        # 3) 문서가 있으면 RAG 수행
        docs = [doc for doc, _ in pairs]
        contents = self._trim_docs_for_llm(docs)  # ★ 컨텍스트 가드
        messages = self.prompt_builder(contents, question)
        return self.llm.chat(messages)

    def generate_answer_with_sources(self, question: str):
        # 0) 스몰토크/의미 약한 입력 차단
        if is_smalltalk(question):
            return FALLBACK_MSG, []

        # 1) 임계값 필터 적용 검색
        pairs = self._retrieve_pairs(question)

        # 2) 최소 문서 수 미만이면 차단
        if len(pairs) < MIN_DOCS:
            return FALLBACK_MSG, []

        # ===== LLM 호출 =====
        docs = [doc for doc, _ in pairs]
        contents = self._trim_docs_for_llm(docs)  # ★ 컨텍스트 가드
        messages = self.prompt_builder(contents, question)
        answer = self.llm.chat(messages)

        # ===== 출처 생성 (source_url 주입) =====
        sources = []
        for doc, score in pairs:
            md = dict(getattr(doc, "metadata", {}) or {})
            gs_path = md.get("gs_path")

            # title 보강
            if gs_path and not md.get("title"):
                md["title"] = os.path.basename(gs_path)

            # score / confidence 보강(원하면 프런트가 metadata에서도 사용 가능)
            md["score"] = float(score)
            md["confidence"] = score_to_confidence(float(score))

            # ★ 서명 URL 주입: 프런트에서 곧바로 열 수 있도록
            if gs_path:
                try:
                    md["source_url"] = signed_url(gs_path, minutes=SIGNED_URL_TTL_MIN, inline=True)
                except Exception:
                    # 실패해도 다른 필드는 유지
                    pass

            sources.append({
                "text": (doc.page_content or "")[:500],
                "score": float(score),
                "confidence": md["confidence"],
                "metadata": md,     # ← 여기 안에 source_url, title, page, gs_path 포함
            })

        return answer, sources
