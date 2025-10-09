# -*- coding: utf-8 -*-
"""
Step 2: Firebase 문서 존재 여부 확인 및 매니페스트 생성
- crawler.py로 게시물 목록 수집
- Firebase Storage에서 기존 문서 확인
- 신규 문서만 매니페스트에 추가
"""
from __future__ import annotations
import json, sys, argparse
from pathlib import Path
from typing import List, Dict, Any
from urllib.parse import urlparse

# 프로젝트 루트를 sys.path에 추가
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from crawler.crawler import fetch_html, build_list_url, parse_list, to_abs_view_url, extract_attachments_from_view
from app.services.storage_utils import list_pdf_keys

def get_existing_firebase_files() -> set[str]:
    """Firebase Storage에 있는 PDF 파일명들을 반환"""
    try:
        pdf_keys = list_pdf_keys()
        # 파일명만 추출 (경로 제거)
        filenames = set()
        for key in pdf_keys:
            filename = Path(key).name.lower()
            filenames.add(filename)
        return filenames
    except Exception as e:
        print(f"[WARN] Firebase 파일 목록 조회 실패: {e}")
        return set()

def extract_filename_from_url(url: str) -> str:
    """URL에서 파일명 추출"""
    parsed = urlparse(url)
    filename = Path(parsed.path).name
    return filename.lower()

def is_new_document(attachment_url: str, existing_files: set[str]) -> bool:
    """Firebase에 없는 새 문서인지 확인"""
    filename = extract_filename_from_url(attachment_url)
    return filename not in existing_files

def build_manifest(top: int = 10, community: str = "B0018") -> List[Dict[str, Any]]:
    """신규 문서만 선별하여 매니페스트 생성"""
    print(f"[STEP2] 게시물 목록 수집 중... (상위 {top}개)")
    
    # 1. 게시물 목록 수집
    list_url, list_params = build_list_url(community, 1)
    try:
        html = fetch_html(list_url, params=list_params)
    except Exception as e:
        print(f"[ERROR] 목록 요청 실패: {e}")
        return []
    
    items = parse_list(html)
    if not items:
        print("[WARN] 게시글 목록을 찾지 못했습니다.")
        return []
    
    print(f"[STEP2] 총 {len(items)}개 게시물 발견")
    
    # 2. Firebase 기존 파일 목록 조회
    print("[STEP2] Firebase 기존 파일 확인 중...")
    existing_files = get_existing_firebase_files()
    print(f"[STEP2] Firebase에 {len(existing_files)}개 파일 존재")
    
    # 3. 상위 N개 게시물의 첨부파일 확인
    manifest = []
    processed_count = 0
    
    for i, (title, href) in enumerate(items[:top], 1):
        if processed_count >= top:
            break
            
        view_url = to_abs_view_url(href)
        try:
            view_html = fetch_html(view_url, referer=list_url)
        except Exception as e:
            print(f"[WARN] {i}. {title} - 상세 요청 실패: {e}")
            continue
        
        attach_urls = extract_attachments_from_view(view_html, view_url)
        if not attach_urls:
            print(f"[SKIP] {i}. {title} - 첨부파일 없음")
            continue
        
        # 각 첨부파일이 신규인지 확인
        new_attachments = []
        for attach_url in attach_urls:
            if is_new_document(attach_url, existing_files):
                new_attachments.append(attach_url)
            else:
                filename = extract_filename_from_url(attach_url)
                print(f"[SKIP] {i}. {title} - {filename} (이미 존재)")
        
        if new_attachments:
            manifest.append({
                "title": title,
                "view_url": view_url,
                "attachment_urls": new_attachments,
                "processed_at": None  # Step 3에서 설정
            })
            print(f"[NEW] {i}. {title} - {len(new_attachments)}개 신규 첨부파일")
            processed_count += 1
    
    return manifest

def main():
    # Windows 콘솔 한글 출력을 위한 인코딩 설정
    import sys
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=10, help="처리할 상위 게시물 수")
    ap.add_argument("--community", default="B0018", help="게시판 communityKey")
    ap.add_argument("--output", default="_work/manifest.json", help="매니페스트 출력 파일")
    args = ap.parse_args()
    
    # 작업 디렉토리 생성
    work_dir = Path("_work")
    work_dir.mkdir(exist_ok=True)
    
    print(f"[STEP2] 시작: top={args.top}, community={args.community}")
    
    # 매니페스트 생성
    manifest = build_manifest(args.top, args.community)
    
    if not manifest:
        print("[STEP2] 신규 문서가 없습니다.")
        # 빈 매니페스트 파일 생성
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return
    
    # 매니페스트 저장
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    
    total_new_files = sum(len(item['attachment_urls']) for item in manifest)
    print(f"[STEP2] 완료: {len(manifest)}개 게시물, {total_new_files}개 신규 파일")
    print(f"[STEP2] 매니페스트 저장: {args.output}")

if __name__ == "__main__":
    main()