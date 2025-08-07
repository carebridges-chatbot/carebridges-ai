import os
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv
load_dotenv()

class VectorStoreHandler:
    def __init__(self, persist_path: str = "db/faiss_index"):
        self.persist_path = persist_path
        self.embedding = OpenAIEmbeddings()
        self.vectorstore = None

    def build_vectorstore(self, documents: List[Document]):
        """
        문서 리스트를 받아 벡터스토어를 생성하고 저장합니다.

        [주의] 이 함수는 ingest 등 초기 벡터 구축용입니다.
        서비스 중에는 사용하지 마세요.
        """
        print("벡터스토어 생성 중...")
        self.vectorstore = FAISS.from_documents(documents, self.embedding)
        self.vectorstore.save_local(self.persist_path)
        print("벡터스토어 저장 완료!")

    def load_vectorstore(self):
        """
        저장된 벡터스토어를 로드합니다.
        """
        if os.path.exists(self.persist_path):
            print("벡터스토어 불러오는 중...")
            self.vectorstore = FAISS.load_local(
                self.persist_path,
                self.embedding,
                allow_dangerous_deserialization=True
            )
            print("벡터스토어 로드 완료!")
        else:
            raise FileNotFoundError(f"'{self.persist_path}'에 저장된 벡터스토어가 없습니다.")

    def search(self, query: str, top_k: int = 5) -> List[Document]:
        """
        쿼리를 기반으로 유사한 문서를 검색합니다.
        """
        if not self.vectorstore:
            raise RuntimeError("벡터스토어가 로드되지 않았습니다. 먼저 load_vectorstore()를 호출하세요.")
        
        print(f"검색 쿼리: {query}")
        results = self.vectorstore.similarity_search(query, k=top_k)
        return results
