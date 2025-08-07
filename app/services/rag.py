# rag.py
from app.db.vectorstore import VectorStoreHandler
from app.services.prompt_builder import build_prompt
from app.services.openai_client import OpenAIClient

class RAGPipeline:
    def __init__(self, top_k: int = 5):
        self.vectorstore = VectorStoreHandler()
        self.vectorstore.load_vectorstore()
        self.prompt_builder = build_prompt
        self.llm = OpenAIClient()
        self.top_k = top_k

    def generate_answer(self, question: str) -> str:
        # 1. 관련 문서 검색
        relevant_docs = self.vectorstore.search(question, top_k=self.top_k)
        doc_texts = [doc.page_content for doc in relevant_docs]

        # 2. 프롬프트 생성
        messages = self.prompt_builder(doc_texts, question)

        # 3. GPT 응답 생성
        answer = self.llm.chat(messages)
        return answer
