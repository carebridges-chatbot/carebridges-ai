from typing import List
from langchain_core.documents import Document
from app.db.vectorstore import VectorStoreHandler


class Retriever:
    def __init__(self, persist_path: str = "db/faiss_index"):
        """
        벡터스토어를 로드하여 검색할 준비를 합니다.
        """
        self.vs_handler = VectorStoreHandler(persist_path)
        self.vs_handler.load_vectorstore()

    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        """
        쿼리를 기반으로 FAISS에서 유사한 문서를 검색합니다.
        """
        results = self.vs_handler.search(query=query, top_k=top_k)
        return results
