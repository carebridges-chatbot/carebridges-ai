# scripts/ingest.py
import os, sys
from pathlib import Path

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())   # ★ .env 먼저 로드

# 프로젝트 루트 인식 (직접 실행/모듈 실행 호환)
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from app.services.storage_utils import list_pdf_keys, download_to_tmp
from scripts.split_documents import split_pdf  # scripts 는 패키지여야 함(__init__.py)

FAISS_SAVE_PATH = "db/faiss_index"

# prefix 정리: 주석/역슬래시 방지
_raw_prefix = os.getenv("FIREBASE_PDF_PREFIX", "")
FIREBASE_PDF_PREFIX = (_raw_prefix or "").replace("\\", "/").strip()
if FIREBASE_PDF_PREFIX.startswith("#"):
    FIREBASE_PDF_PREFIX = ""

# === 임베딩 입력 길이 가드(문자 기준; 토큰 측정이 없을 때 보수적 상한) ===
# 개별 텍스트 길이를 타이트하게 제한 (대략 2k~3k 토큰 급)
MAX_EMBED_CHARS = int(os.getenv("MAX_EMBED_CHARS", "8000"))
MIN_CHARS_TO_KEEP = int(os.getenv("MIN_CHARS_TO_KEEP", "100"))

# === 배치/토큰 가드 ===
EMBED_BATCH = int(os.getenv("EMBED_BATCH", "80"))  # 1차: 개수 기준 분할
PER_REQUEST_TOKEN_BUDGET = int(os.getenv("PER_REQUEST_TOKEN_BUDGET", "280000"))  # 요청당 토큰 총합 한도(버퍼 포함)
CHARS_PER_TOKEN = float(os.getenv("CHARS_PER_TOKEN", "4"))  # 1토큰≈4문자 가정

def estimate_tokens(s: str) -> int:
    return int(len(s) / CHARS_PER_TOKEN) if s else 0

def yield_token_capped_batches(texts, metas, max_tokens: int):
    """요청당 토큰 총합이 max_tokens를 넘지 않도록 분할."""
    cur_texts, cur_metas, cur_tokens = [], [], 0
    for t, m in zip(texts, metas):
        t_tokens = estimate_tokens(t)
        if t_tokens > max_tokens:
            # 단일 텍스트가 예산을 넘더라도 자른 상태라면 단독 전송
            if cur_texts:
                yield cur_texts, cur_metas
                cur_texts, cur_metas, cur_tokens = [], [], 0
            yield [t], [m]
            continue

        if cur_tokens + t_tokens > max_tokens and cur_texts:
            yield cur_texts, cur_metas
            cur_texts, cur_metas, cur_tokens = [], [], 0

        cur_texts.append(t)
        cur_metas.append(m)
        cur_tokens += t_tokens

    if cur_texts:
        yield cur_texts, cur_metas

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

        # split_pdf: 문자열 리스트 or Document 리스트 모두 처리
        chunks = split_pdf(local_pdf) or []

        normalized = []
        if chunks and isinstance(chunks[0], Document):
            for d in chunks:
                meta = dict(getattr(d, "metadata", {}) or {})
                meta.setdefault("title", Path(key).name)
                meta["gs_path"] = key
                d.metadata = meta
                normalized.append(d)
        else:
            for t in chunks:
                normalized.append(
                    Document(
                        page_content=str(t),
                        metadata={"title": Path(key).name, "gs_path": key},
                    )
                )

        # ★ 임베딩 입력 하드컷
        trimmed = []
        for d in normalized:
            txt = (d.page_content or "").strip()
            if not txt:
                continue
            if len(txt) > MAX_EMBED_CHARS:
                txt = txt[:MAX_EMBED_CHARS]
            if len(txt) >= MIN_CHARS_TO_KEEP:
                d.page_content = txt
                trimmed.append(d)

        print(f"→ {len(trimmed)}개 청크(임베딩 입력 길이 가드 적용)")
        all_docs.extend(trimmed)

        # 임시파일 정리(선택)
        try:
            Path(local_pdf).unlink(missing_ok=True)
        except Exception:
            pass

    print(f"\n총 {len(all_docs)}개 청크 준비 완료")
    if not all_docs:
        print("※ 생성된 청크가 없습니다. split_pdf 동작을 확인하세요.")
        return

    print("OpenAI 임베딩 생성...")
    # ⚠️ batch_size 인자 넣지 마세요 (SDK로 흘러가 오류)
    embeddings = OpenAIEmbeddings(
        # model="text-embedding-3-small",  # 필요 시 명시
        # max_retries=6,                   # 옵션
        # request_timeout=60,              # 옵션
    )

    print("FAISS 벡터스토어 생성/저장...")
    vectorstore = None
    n = len(all_docs)

    # 1차: 개수 기준 배치
    for i in range(0, n, EMBED_BATCH):
        batch_docs = all_docs[i:i + EMBED_BATCH]
        print(f"  • 임베딩 배치 처리(개수): {i} ~ {min(i + EMBED_BATCH, n)} / {n}")

        texts = [d.page_content or "" for d in batch_docs]
        metas = [d.metadata or {} for d in batch_docs]

        # 2차: 요청당 토큰 총합 예산으로 추가 분할
        for sub_texts, sub_metas in yield_token_capped_batches(texts, metas, PER_REQUEST_TOKEN_BUDGET):
            sub_docs = [Document(page_content=t, metadata=m) for t, m in zip(sub_texts, sub_metas)]
            if vectorstore is None:
                vectorstore = FAISS.from_documents(sub_docs, embedding=embeddings)
            else:
                vectorstore.add_documents(sub_docs)

    vectorstore.save_local(FAISS_SAVE_PATH)
    print("완료! ->", FAISS_SAVE_PATH)

if __name__ == "__main__":
    main()
