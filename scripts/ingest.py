import os
from dotenv import load_dotenv
from pathlib import Path
from split_documents import split_pdf
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

load_dotenv()

# 경로 설정
PDF_DIR = Path("data/FAQ")
FAISS_SAVE_PATH = "db/faiss_index"

def main():
    all_chunks = []

    print("PDF에서 텍스트 분할 중...")
    for pdf_file in PDF_DIR.glob("*.pdf"):
        print(f"-> cjflwnd: {pdf_file.name}")
        chunks = split_pdf(str(pdf_file))
        print(f"    -{len(chunks)}개 청크 생성 완료")
        all_chunks.extend(chunks)
        
    
    print(f"\n총 {len(all_chunks)}개의 청크 생성 완료")

    print("OpenAI 임베딩 모델 로드 중...")
    embeddings = OpenAIEmbeddings()

    print("FAISS 벡터스토어 생성 중...")
    vectorstore = FAISS.from_documents(all_chunks, embedding=embeddings)

    print(f"FAISS 벡터스토어를 '{FAISS_SAVE_PATH}'에 저장 중...")
    vectorstore.save_local(FAISS_SAVE_PATH)
    print("전체 PDF 임베딩 및 저장 완료!")

if __name__ == "__main__":
    main()
