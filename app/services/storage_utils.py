# app/services/storage_utils.py
import os, tempfile, json, base64
from datetime import timedelta
from dotenv import load_dotenv, find_dotenv
from google.cloud import storage
from google.oauth2 import service_account

load_dotenv(find_dotenv())   # .env 로드

# --- 인증 클라이언트 생성: JSON → B64 → 파일경로 → 기본 순 ---
def _make_client() -> storage.Client:
    # 1) .env에 JSON 원문이 들어온 경우
    sa_json = os.getenv("FIREBASE_SA_JSON")
    if sa_json:
        try:
            info = json.loads(sa_json)
        except json.JSONDecodeError:
            # \n 등이 이스케이프된 형태로 들어온 경우 처리
            info = json.loads(sa_json.encode("utf-8").decode("unicode_escape"))
        creds = service_account.Credentials.from_service_account_info(info)
        return storage.Client(credentials=creds, project=info.get("project_id"))

    # 2) .env에 JSON을 base64로 넣은 경우
    sa_b64 = os.getenv("FIREBASE_SA_B64")
    if sa_b64:
        info = json.loads(base64.b64decode(sa_b64))
        creds = service_account.Credentials.from_service_account_info(info)
        return storage.Client(credentials=creds, project=info.get("project_id"))

    # 3) 파일 경로 방식 (기존)
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if cred_path:
        return storage.Client.from_service_account_json(cred_path)

    # 4) ADC(인스턴스 메타데이터 등)
    return storage.Client()

_client = _make_client()

def _bucket_name() -> str:
    name = (os.getenv("FIREBASE_BUCKET", "") or "").strip()
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
