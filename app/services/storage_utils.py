# app/services/storage_utils.py
import os, tempfile
from datetime import timedelta
from dotenv import load_dotenv, find_dotenv
from google.cloud import storage

load_dotenv(find_dotenv())           # ★ 여기서도 .env 로드(이중 안전망)

_client = storage.Client()

def _bucket_name() -> str:
    name = os.getenv("FIREBASE_BUCKET", "").strip()
    if not name or name.startswith("gs://"):
        raise RuntimeError(
            f"FIREBASE_BUCKET 환경변수 확인 필요: 현재='{name}'. "
            "버킷 이름만 넣으세요 (예: carebridges-c689d.firebasestorage.app)."
        )
    return name

def list_pdf_keys(prefix: str = "") -> list[str]:
    prefix = (prefix or "").replace("\\", "/").strip()
    bucket = _client.bucket(_bucket_name())
    return [
        b.name for b in _client.list_blobs(bucket, prefix=prefix)
        if b.name.lower().endswith(".pdf")
    ]

def download_to_tmp(gs_path: str) -> str:
    bucket = _client.bucket(_bucket_name())
    blob = bucket.blob(gs_path)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    blob.download_to_filename(tmp.name)
    return tmp.name

def signed_url(gs_path: str, minutes: int = 10, inline: bool = True) -> str:
    bucket = _client.bucket(_bucket_name())
    blob = bucket.blob(gs_path)
    return blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=minutes),
        method="GET",
        response_disposition="inline" if inline else "attachment",
    )
