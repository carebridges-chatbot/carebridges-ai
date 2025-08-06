import os
from dotenv import load_dotenv
load_dotenv() # .env 파일 로드됨

from split_documents import split_pdf
from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# 경로 설정
PDF_PATH = "data/제1장_장기요양인정_신청.pdf (248037 Bytes)"
FAISS_SAVE_PATH = "db/faiss_index"

def main():
    print("PDF에서 텍스트 분할 중...")
    chunks = split_pdf(PDF_PATH)
    print(f"총 {len(chunks)}개의 청크 생성 완료")

    print("OpenAI 임베딩 모델 로드 중...")
    embeddings = OpenAIEmbeddings()

    print("FAISS 벡터스토어 생성 중...")
    vectorstore = FAISS.from_documents(chunks, embedding=embeddings)

    print(f"FAISS 벡터스토어를 '{FAISS_SAVE_PATH}'에 저장 중...")
    vectorstore.save_local(FAISS_SAVE_PATH)
    print("벡터 DB 생성 완료!")

if __name__ == "__main__":
    main()
