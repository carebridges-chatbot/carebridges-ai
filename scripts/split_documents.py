#from langchain.document_loaders import PyPDFLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
from langchain.schema import Document


def split_pdf(file_path: str, chunk_size: int = 500, chunk_overlap: int = 100) -> List[Document]:
    """
    주어진 PDF 파일을 로드하고, 텍스트를 분할하여 Document 리스트로 반환합니다.

    Args:
        file_path (str): PDF 파일 경로
        chunk_size (int): 하나의 청크 길이 (기본값: 500자)
        chunk_overlap (int): 청크 간 겹치는 길이 (기본값: 100자)

    Returns:
        List[Document]: 분할된 문서 청크 리스트
    """
    # 1. 문서 로드
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    # 2. 텍스트 분할기 설정
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    # 3. 문서 분할
    chunks = splitter.split_documents(documents)

    return chunks
