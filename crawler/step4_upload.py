# -*- coding: utf-8 -*-
"""
Step 4: Firebase Storage에 파일 업로드
- 처리된 파일들을 Firebase Storage에 업로드
- 업로드 성공/실패 로그 기록
"""
from __future__ import annotations
import json, sys, argparse
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# 프로젝트 루트를 sys.path에 추가
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.storage_utils import _client, _bucket_name

def upload_file_to_firebase(local_path: str, remote_path: str) -> bool:
    """파일을 Firebase Storage에 업로드"""
    try:
        client = _client
        bucket_name = _bucket_name()
        
        # 로컬 파일 확인
        local_file = Path(local_path)
        if not local_file.exists():
            print(f"[ERROR] 로컬 파일이 없습니다: {local_path}")
            return False
        
        # Firebase Storage에 업로드
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(remote_path)
        
        # 파일 업로드
        blob.upload_from_filename(str(local_file))
        
        # 메타데이터 설정
        blob.metadata = {
            'uploaded_at': datetime.now().isoformat(),
            'source': 'crawler_pipeline',
            'original_filename': local_file.name
        }
        blob.patch()
        
        print(f"[UPLOAD] {local_file.name} → gs://{bucket_name}/{remote_path}")
        return True
        
    except Exception as e:
        print(f"[ERROR] 업로드 실패 {local_path}: {e}")
        return False

def generate_remote_path(filename: str, title: str) -> str:
    """Firebase Storage 경로 생성"""
    # 제목을 안전한 경로로 변환
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_title = safe_title.replace(' ', '_')[:50]  # 길이 제한
    
    # 날짜별 폴더 구조
    today = datetime.now().strftime("%Y%m%d")
    return f"crawled_documents/{today}/{safe_title}/{filename}"

def process_upload(processed_files_path: Path) -> List[Dict[str, Any]]:
    """처리된 파일들을 Firebase에 업로드"""
    if not processed_files_path.exists():
        print(f"[ERROR] 처리된 파일 목록이 없습니다: {processed_files_path}")
        return []
    
    with open(processed_files_path, 'r', encoding='utf-8') as f:
        processed_files = json.load(f)
    
    if not processed_files:
        print("[INFO] 업로드할 파일이 없습니다.")
        return []
    
    print(f"[STEP4] {len(processed_files)}개 게시물의 파일 업로드 시작")
    
    upload_results = []
    
    for i, item in enumerate(processed_files, 1):
        title = item['title']
        files = item['files']
        
        print(f"\n[STEP4] {i}. {title}")
        
        item_results = []
        
        for file_info in files:
            local_path = file_info['local_path']
            filename = file_info['filename']
            
            # Firebase Storage 경로 생성
            remote_path = generate_remote_path(filename, title)
            
            # 파일 업로드
            if upload_file_to_firebase(local_path, remote_path):
                item_results.append({
                    'filename': filename,
                    'local_path': local_path,
                    'remote_path': remote_path,
                    'size': file_info['size'],
                    'uploaded_at': datetime.now().isoformat(),
                    'status': 'success'
                })
            else:
                item_results.append({
                    'filename': filename,
                    'local_path': local_path,
                    'remote_path': remote_path,
                    'size': file_info['size'],
                    'uploaded_at': None,
                    'status': 'failed'
                })
        
        if item_results:
            upload_results.append({
                'title': title,
                'view_url': item['view_url'],
                'files': item_results,
                'uploaded_at': datetime.now().isoformat()
            })
            
            success_count = sum(1 for f in item_results if f['status'] == 'success')
            print(f"[STEP4] {i}. {title} - {success_count}/{len(item_results)}개 파일 업로드 완료")
    
    return upload_results

def main():
    # Windows 콘솔 한글 출력을 위한 인코딩 설정
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed-files", default="_work/processed_files.json", help="처리된 파일 목록")
    ap.add_argument("--output", default="_work/upload_results.json", help="업로드 결과 출력 파일")
    args = ap.parse_args()
    
    print(f"[STEP4] 시작: processed_files={args.processed_files}")
    
    # 파일 업로드
    upload_results = process_upload(Path(args.processed_files))
    
    if not upload_results:
        print("[STEP4] 업로드할 파일이 없습니다.")
        return
    
    # 업로드 결과 저장
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(upload_results, f, ensure_ascii=False, indent=2)
    
    # 통계 출력
    total_files = sum(len(item['files']) for item in upload_results)
    success_files = sum(1 for item in upload_results for f in item['files'] if f['status'] == 'success')
    
    print(f"[STEP4] 완료: {len(upload_results)}개 게시물, {success_files}/{total_files}개 파일 업로드 성공")
    print(f"[STEP4] 업로드 결과: {args.output}")

if __name__ == "__main__":
    main()