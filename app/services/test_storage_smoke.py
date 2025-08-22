# app/services/test_storage_smoke.py
import os
from datetime import timedelta
from dotenv import load_dotenv, find_dotenv

# 클라이언트 팩토리 재사용(환경변수 JSON/B64/파일 모두 지원)
from app.services.storage_utils import _make_client

load_dotenv(find_dotenv())

bucket_name = os.getenv("FIREBASE_BUCKET")
prefix = (os.getenv("FIREBASE_PDF_PREFIX", "") or "").replace("\\", "/")

assert bucket_name and not bucket_name.startswith("gs://"), \
    "FIREBASE_BUCKET에는 'gs://'를 빼고 버킷 이름만 넣으세요."

# 어떤 인증이 쓰였는지 힌트 출력(디버그)
if os.getenv("FIREBASE_SA_JSON"):
    print("[auth] using FIREBASE_SA_JSON")
elif os.getenv("FIREBASE_SA_B64"):
    print("[auth] using FIREBASE_SA_B64")
elif os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    print(f"[auth] using GOOGLE_APPLICATION_CREDENTIALS={os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
else:
    print("[auth] using default credentials (ADC)")

client = _make_client()

pdfs = [b for b in client.list_blobs(bucket_name, prefix=prefix)
        if b.name.lower().endswith(".pdf")]

print("Bucket:", bucket_name)
print("Prefix:", repr(prefix))
print("PDF keys:", [b.name for b in pdfs])

if pdfs:
    url = pdfs[0].generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=10),
        method="GET",
        response_disposition="inline"
    )
    print("signed url sample:", url)
else:
    print("해당 prefix 아래에 .pdf가 없습니다.")
