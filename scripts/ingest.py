# scripts/ingest.py
import os, sys
from pathlib import Path

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())   # ★ .env를 가장 먼저 로드!

# 프로젝트 루트 인식 (직접 실행/모듈 실행 모두 호환)
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
# ★ LC 0.2 권장 네임스페이스로 통일
from langchain_core.documents import Document

from app.services.storage_utils import list_pdf_keys, download_to_tmp
from scripts.split_documents import split_pdf  # scripts 가 패키지(__init__.py)여야 함

FAISS_SAVE_PATH = "db/faiss_index"

# prefix 정리: 주석/역슬래시 방지
_raw_prefix = os.getenv("FIREBASE_PDF_PREFIX", "")
FIREBASE_PDF_PREFIX = (_raw_prefix or "").replace("\\", "/").strip()
if FIREBASE_PDF_PREFIX.startswith("#"):
    FIREBASE_PDF_PREFIX = ""

def main():
    all_docs = []

    print("Firebase Storage에서 PDF 목록 조회...")
    pdf_keys = list_pdf_keys(prefix=FIREBASE_PDF_PREFIX)
    print(f"→ {len(pdf_keys)}개 발견")
    if not pdf_keys:
        print("※ PDF가 없습니다. 콘솔의 경로/파일명을 다시 확인하세요.")
        return

    for key in pdf_keys:
        print(f"\n[다운로드] gs://{os.getenv('FIREBASE_BUCKET')}/{key}")
        local_pdf = download_to_tmp(key)

        # split_pdf가 문자열 리스트 or Document 리스트 모두 처리
        chunks = split_pdf(local_pdf) or []

        normalized = []
        if chunks and isinstance(chunks[0], Document):
            # 이미 Document 객체인 경우: 메타데이터만 보강
            for d in chunks:
                meta = dict(getattr(d, "metadata", {}) or {})
                meta.setdefault("title", Path(key).name)
                meta["gs_path"] = key
                d.metadata = meta
                normalized.append(d)
        else:
            # 문자열 청크인 경우: Document로 감싸기
            for t in chunks:
                normalized.append(
                    Document(
                        page_content=str(t),
                        metadata={"title": Path(key).name, "gs_path": key},
                    )
                )

        print(f"→ {len(normalized)}개 청크")
        all_docs.extend(normalized)

        # (선택) 임시파일 정리
        try:
            Path(local_pdf).unlink(missing_ok=True)
        except Exception:
            pass

    print(f"\n총 {len(all_docs)}개 청크 준비 완료")
    if not all_docs:
        print("※ 생성된 청크가 없습니다. split_pdf 동작을 확인하세요.")
        return

    print("OpenAI 임베딩 생성...")
    embeddings = OpenAIEmbeddings()  # OPENAI_API_KEY 필요

    print("FAISS 벡터스토어 생성/저장...")
    vectorstore = FAISS.from_documents(all_docs, embedding=embeddings)
    vectorstore.save_local(FAISS_SAVE_PATH)
    print("완료! ->", FAISS_SAVE_PATH)

if __name__ == "__main__":
    main()
