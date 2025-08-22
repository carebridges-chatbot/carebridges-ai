# app/services/test_storage_smoke.py
import os
from datetime import timedelta
from dotenv import load_dotenv
from google.cloud import storage

load_dotenv()

bucket_name = os.getenv("FIREBASE_BUCKET")
cred = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
prefix = (os.getenv("FIREBASE_PDF_PREFIX", "") or "").replace("\\", "/")

assert bucket_name and not bucket_name.startswith("gs://")
assert cred and os.path.exists(cred), f"키 파일 경로 확인: {cred}"

client = storage.Client()
pdfs = [b for b in client.list_blobs(bucket_name, prefix=prefix) if b.name.lower().endswith(".pdf")]

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
    print("루트에 .pdf가 없습니다. 콘솔 파일명(정확한 철자) 확인하세요.")
