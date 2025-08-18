import os
from typing import List, Tuple, Dict, Any
from langchain_core.documents import Document
from app.db.vectorstore import VectorStoreHandler
from app.services.prompt_builder import build_prompt
from app.services.openai_client import OpenAIClient

# ===== 설정 =====
THRESHOLD_DISTANCE = float(os.getenv("THRESHOLD_DISTANCE", "0.32"))  # 작을수록 유사(거리)
MIN_DOCS = int(os.getenv("MIN_DOCS", "1"))                            # 통과 문서 최소 개수
FALLBACK_MSG = os.getenv("FALLBACK_MSG", "사회복지와 관련된 질문만 해주세요.")

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
        messages = self.prompt_builder([d.page_content for d in docs], question)
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

        # 3) 문서가 있으면 RAG 수행
        docs = [doc for doc, _ in pairs]
        messages = self.prompt_builder([d.page_content for d in docs], question)
        answer = self.llm.chat(messages)

        sources = [{
            "text": doc.page_content[:500],
            "score": float(score),
            "confidence": score_to_confidence(float(score)),
            "metadata": getattr(doc, "metadata", None),
        } for doc, score in pairs]

        return answer, sources
