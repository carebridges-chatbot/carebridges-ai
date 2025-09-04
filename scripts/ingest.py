# scripts/ingest.py
import os, sys
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from app.services.storage_utils import list_pdf_keys, download_to_tmp
from scripts.split_documents import split_pdf

FAISS_SAVE_PATH = "db/faiss_index"

_raw_prefix = os.getenv("FIREBASE_PDF_PREFIX", "")
FIREBASE_PDF_PREFIX = (_raw_prefix or "").replace("\\", "/").strip()
if FIREBASE_PDF_PREFIX.startswith("#"):
    FIREBASE_PDF_PREFIX = ""

EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
BATCH = int(os.getenv("INGEST_BATCH", "64"))

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

        chunks = split_pdf(local_pdf) or []

        normalized = []
        if chunks and isinstance(chunks[0], Document):
            for d in chunks:
                meta = dict(getattr(d, "metadata", {}) or {})
                meta.setdefault("title", Path(key).name)
                meta["gs_path"] = key
                d.metadata = meta
                if (d.page_content or "").strip():
                    normalized.append(d)
        else:
            for t in chunks:
                t = (t or "").strip()
                if not t:
                    continue
                normalized.append(
                    Document(
                        page_content=str(t),
                        metadata={"title": Path(key).name, "gs_path": key},
                    )
                )

        print(f"→ {len(normalized)}개 청크")
        all_docs.extend(normalized)

        try:
            Path(local_pdf).unlink(missing_ok=True)
        except Exception:
            pass

    print(f"\n총 {len(all_docs)}개 청크 준비 완료")
    if not all_docs:
        print("※ 생성된 청크가 없습니다. split_pdf 동작을 확인하세요.")
        return

    print(f"OpenAI 임베딩 생성 (model={EMBED_MODEL})...")
    embeddings = OpenAIEmbeddings(model=EMBED_MODEL)

    print(f"FAISS 벡터스토어 생성/저장 (배치={BATCH})...")
    vectorstore = None
    total = len(all_docs)
    done = 0

    for i in range(0, total, BATCH):
        batch = all_docs[i:i + BATCH]
        if vectorstore is None:
            vectorstore = FAISS.from_documents(batch, embedding=embeddings)
        else:
            vectorstore.add_documents(batch)

        done += len(batch)
        print(f"  - 진행: {done}/{total}")

        # 진행 중 중간 저장(안전)
        if (i // BATCH) % 5 == 4:
            vectorstore.save_local(FAISS_SAVE_PATH)

    vectorstore.save_local(FAISS_SAVE_PATH)
    print("완료! ->", FAISS_SAVE_PATH)

if __name__ == "__main__":
    main()
