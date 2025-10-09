# -*- coding: utf-8 -*-
"""
Step 3: 파일 다운로드 및 HWP → PDF 변환
- 매니페스트에서 첨부파일 다운로드
- HWP 파일을 PDF로 변환
- 다운로드된 파일들을 임시 디렉토리에 저장
"""
from __future__ import annotations
import json, sys, argparse, os, tempfile, subprocess
from pathlib import Path
from typing import List, Dict, Any
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

# 프로젝트 루트를 sys.path에 추가
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def download_file(url: str, output_path: Path) -> bool:
    """파일 다운로드"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
            "Referer": "https://www.longtermcare.or.kr/"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Content-Disposition에서 파일명 추출 시도 (한글 파일명 무시)
        content_disposition = response.headers.get('Content-Disposition', '')
        if 'filename=' in content_disposition:
            # filename="파일명.pdf" 형태에서 파일명 추출
            import re
            match = re.search(r'filename[^;=\n]*=(([\'"]).*?\2|[^;\n]*)', content_disposition)
            if match:
                filename = match.group(1).strip('"\'')
                # 한글 파일명은 무시하고 확장자만 추출
                if '.' in filename:
                    ext = '.' + filename.split('.')[-1]
                    output_path = output_path.with_suffix(ext)
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"[DOWNLOAD] {url} → {output_path.name}")
        return True
        
    except Exception as e:
        print(f"[ERROR] 다운로드 실패 {url}: {e}")
        return False

def sanitize_filename(filename: str) -> str:
    """파일명을 안전한 형태로 변환"""
    import re
    # 한글과 특수문자를 제거하고 영문/숫자만 유지
    safe_name = re.sub(r'[^\w\-_\.]', '_', filename)
    # 연속된 언더스코어를 하나로
    safe_name = re.sub(r'_+', '_', safe_name)
    # 시작과 끝의 언더스코어 제거
    safe_name = safe_name.strip('_')
    # 빈 문자열이면 기본값 사용
    if not safe_name:
        safe_name = "downloaded_file"
    return safe_name

def convert_hwp_to_pdf(hwp_path: Path, pdf_path: Path) -> bool:
    """HWP 파일을 PDF로 변환 (여러 방법 시도)"""
    
    # 방법 1: LibreOffice 시도
    try:
        cmd = [
            "libreoffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", str(pdf_path.parent),
            str(hwp_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            expected_pdf = pdf_path.parent / f"{hwp_path.stem}.pdf"
            if expected_pdf.exists():
                expected_pdf.rename(pdf_path)
                print(f"[CONVERT] LibreOffice: {hwp_path.name} → {pdf_path.name}")
                return True
    except FileNotFoundError:
        pass  # LibreOffice가 없으면 다음 방법 시도
    except Exception as e:
        print(f"[WARN] LibreOffice 변환 실패: {e}")
    
    # 방법 2: Python 라이브러리로 HWP 내용 추출 후 PDF 생성
    try:
        return convert_hwp_with_python(hwp_path, pdf_path)
    except Exception as e:
        print(f"[WARN] Python HWP 변환 실패: {e}")
    
    # 방법 3: 온라인 변환 API 시도 (선택사항)
    # try:
    #     return convert_hwp_online(hwp_path, pdf_path)
    # except Exception as e:
    #     print(f"[WARN] 온라인 변환 실패: {e}")
    
    # 모든 방법 실패시 원본 파일을 PDF로 복사 (임시 해결책)
    print(f"[WARN] HWP 변환 불가. 원본 파일을 그대로 유지: {hwp_path.name}")
    return False

def convert_hwp_with_python(hwp_path: Path, pdf_path: Path) -> bool:
    """Python 라이브러리를 사용한 HWP → PDF 변환"""
    try:
        # olefile을 사용한 HWP 파일 분석
        import olefile
        
        if not olefile.isOleFile(str(hwp_path)):
            print(f"[WARN] HWP 파일이 아닙니다: {hwp_path.name}")
            return False
        
        # HWP 파일에서 텍스트 추출
        with olefile.OleFileIO(str(hwp_path)) as ole:
            # HWP 파일 구조 분석
            if ole._olestreams:
                # 간단한 텍스트 추출 시도
                text_content = ""
                for stream_name in ole._olestreams:
                    if 'BodyText' in stream_name or 'Section' in stream_name:
                        try:
                            stream_data = ole.openfile(stream_name).read()
                            # 바이너리 데이터에서 텍스트 추출 시도
                            text_content += stream_data.decode('utf-8', errors='ignore')
                        except:
                            continue
                
                if text_content.strip():
                    # 추출된 텍스트로 간단한 PDF 생성
                    from reportlab.pdfgen import canvas
                    from reportlab.lib.pagesizes import letter
                    from reportlab.pdfbase import pdfmetrics
                    from reportlab.pdfbase.ttfonts import TTFont
                    
                    # 한글 폰트 등록 (시스템 폰트 사용)
                    try:
                        pdfmetrics.registerFont(TTFont('NanumGothic', 'C:/Windows/Fonts/malgun.ttf'))
                        font_name = 'NanumGothic'
                    except:
                        font_name = 'Helvetica'
                    
                    c = canvas.Canvas(str(pdf_path), pagesize=letter)
                    width, height = letter
                    
                    # 텍스트를 페이지에 맞게 분할
                    lines = text_content.split('\n')
                    y_position = height - 50
                    
                    for line in lines[:50]:  # 최대 50줄만 처리
                        if y_position < 50:
                            c.showPage()
                            y_position = height - 50
                        
                        c.setFont(font_name, 10)
                        c.drawString(50, y_position, line[:80])  # 한 줄당 80자 제한
                        y_position -= 15
                    
                    c.save()
                    print(f"[CONVERT] Python: {hwp_path.name} → {pdf_path.name}")
                    return True
                    
    except ImportError:
        print("[WARN] olefile 또는 reportlab 라이브러리가 설치되지 않음")
        return False
    except Exception as e:
        print(f"[WARN] Python HWP 변환 실패: {e}")
        return False
    
    return False

def get_file_extension(url: str) -> str:
    """URL에서 파일 확장자 추출"""
    parsed = urlparse(url)
    path = parsed.path.lower()
    
    if '.pdf' in path:
        return '.pdf'
    elif '.hwp' in path:
        return '.hwp'
    elif '.hwpx' in path:
        return '.hwpx'
    else:
        # Content-Type 헤더 확인
        try:
            response = requests.head(url, timeout=10)
            content_type = response.headers.get('Content-Type', '').lower()
            if 'pdf' in content_type:
                return '.pdf'
            elif 'hwp' in content_type or 'hancom' in content_type:
                return '.hwp'
        except:
            pass
        
        return '.pdf'  # 기본값

def process_manifest(manifest_path: Path, work_dir: Path) -> List[Dict[str, Any]]:
    """매니페스트 처리 및 파일 다운로드/변환"""
    if not manifest_path.exists():
        print(f"[ERROR] 매니페스트 파일이 없습니다: {manifest_path}")
        return []
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    if not manifest:
        print("[INFO] 처리할 항목이 없습니다.")
        return []
    
    print(f"[STEP3] {len(manifest)}개 게시물 처리 시작")
    
    processed_files = []
    
    for i, item in enumerate(manifest, 1):
        title = item['title']
        attachment_urls = item['attachment_urls']
        
        print(f"\n[STEP3] {i}. {title}")
        
        item_files = []
        
        for j, url in enumerate(attachment_urls, 1):
            # 파일 확장자 확인
            ext = get_file_extension(url)
            
            # 간단한 파일명 생성 (한글 문제 해결)
            temp_filename = f"file_{i}_{j}{ext}"
            temp_path = work_dir / temp_filename
            
            # 파일 다운로드
            if not download_file(url, temp_path):
                continue
            
            if not temp_path.exists():
                continue
            
            # HWP 파일인 경우 PDF로 변환
            if ext in ['.hwp', '.hwpx']:
                pdf_filename = f"converted_{i}_{j}.pdf"
                pdf_path = work_dir / pdf_filename
                
                if convert_hwp_to_pdf(temp_path, pdf_path):
                    # 원본 HWP 파일 삭제
                    temp_path.unlink()
                    final_path = pdf_path
                    final_ext = '.pdf'
                else:
                    # 변환 실패시 원본 유지
                    final_path = temp_path
                    final_ext = ext
            else:
                final_path = temp_path
                final_ext = ext
            
            if final_path.exists():
                item_files.append({
                    'original_url': url,
                    'local_path': str(final_path),
                    'filename': final_path.name,
                    'extension': final_ext,
                    'size': final_path.stat().st_size
                })
        
        if item_files:
            processed_files.append({
                'title': title,
                'view_url': item['view_url'],
                'files': item_files,
                'processed_at': None  # Step 4에서 설정
            })
            print(f"[STEP3] {i}. {title} - {len(item_files)}개 파일 처리 완료")
        else:
            print(f"[STEP3] {i}. {title} - 처리된 파일 없음")
    
    return processed_files

def main():
    # Windows 콘솔 한글 출력을 위한 인코딩 설정
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="_work/manifest.json", help="매니페스트 파일 경로")
    ap.add_argument("--work-dir", default="_work/downloads", help="다운로드 작업 디렉토리")
    ap.add_argument("--output", default="_work/processed_files.json", help="처리된 파일 목록 출력")
    args = ap.parse_args()
    
    # 작업 디렉토리 생성
    work_dir = Path(args.work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[STEP3] 시작: manifest={args.manifest}, work_dir={args.work_dir}")
    
    # 매니페스트 처리
    processed_files = process_manifest(Path(args.manifest), work_dir)
    
    if not processed_files:
        print("[STEP3] 처리된 파일이 없습니다.")
        return
    
    # 처리된 파일 목록 저장
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(processed_files, f, ensure_ascii=False, indent=2)
    
    total_files = sum(len(item['files']) for item in processed_files)
    print(f"[STEP3] 완료: {len(processed_files)}개 게시물, {total_files}개 파일 처리")
    print(f"[STEP3] 처리된 파일 목록: {args.output}")

if __name__ == "__main__":
    main()