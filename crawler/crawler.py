# -*- coding: utf-8 -*-
"""
Step 3: 법령자료실 상위 게시글 제목/상세 링크 파싱 (실엔드포인트 직접 접근)
- moveBoardView는 라우터라 목록이 비어 보일 수 있으므로,
  실제 목록/뷰 엔드포인트인 cms/board/board/Board.jsp로 바로 붙는다.
- 출력: 상위 N개 (제목, 절대경로 상세링크)  -> 다음 스텝에서 첨부파일 추출/다운로드 연결 예정.
"""

from __future__ import annotations
import sys
import argparse
import re
from typing import List, Tuple
from urllib.parse import urljoin, urlencode
import requests
from bs4 import BeautifulSoup

BASE = "https://www.longtermcare.or.kr"
LIST_PATH = "/npbs/cms/board/board/Board.jsp"
VIEW_PATH = "/npbs/cms/board/board/Board.jsp"  # act=VIEW 동일 경로

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"

def fetch_html(url: str, params: dict | None = None, referer: str | None = None) -> str:
    with requests.Session() as s:
        s.headers.update({
            "User-Agent": UA,
            "Accept-Language": "ko,en;q=0.8",
        })
        if referer:
            s.headers.update({"Referer": referer})
        r = s.get(url, params=params, timeout=15)
        r.raise_for_status()
        r.encoding = r.apparent_encoding or "utf-8"
        return r.text

def parse_list(html: str) -> List[Tuple[str, str]]:
    """
    목록 페이지에서 <td headers="board_title"> 내부 <a>의 (제목, href) 추출.
    반환 href는 절대 URL이 아닌 원문 그대로.
    """
    soup = BeautifulSoup(html, "lxml")
    title_tds = soup.find_all("td", attrs={"headers": re.compile(r"\bboard_title\b", re.I)})
    out: List[Tuple[str, str]] = []
    for td in title_tds:
        a = td.find("a")
        if not a:
            continue
        title = (a.get_text(separator=" ", strip=True) or "").replace("\xa0", " ").strip()
        href = (a.get("href") or "").strip()
        if not href:
            continue
        out.append((title, href))
    return out

def to_abs_view_url(href: str) -> str:
    """
    목록의 a[href]는 보통 '...Board.jsp?act=VIEW&boardId=...&communityKey=...' 형식
    상대/쿼리만 온 경우를 포함해 절대 URL로 정규화.
    """
    if href.lower().startswith("http"):
        return href
    # href가 '?act=VIEW&boardId=...' 처럼 쿼리만 올 수도 있음
    if href.startswith("?"):
        return BASE + VIEW_PATH + href
    # 상대경로일 경우
    return urljoin(BASE + VIEW_PATH, href)

def build_list_url(community_key: str = "B0018", page_num: int = 1) -> Tuple[str, dict]:
    """
    실 목록 엔드포인트와 파라미터 구성.
    """
    url = BASE + LIST_PATH
    params = {
        "act": "LIST",
        "communityKey": community_key,
        "pageNum": str(page_num),
        "searchType": "ALL",
        "searchWord": "",
        "list_start_date": "",
        "list_end_date": "",
        "pageSize": "",           # 사이트 기본 페이지크기 사용
        "list_show_answer": "N",
        "branch_id": "",
        "branch_child_id": "",
    }
    return url, params

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--community", default="B0018", help="communityKey (기본: 법령자료실 B0018)")
    ap.add_argument("--top", type=int, default=5, help="상위 몇 개 출력할지")
    ap.add_argument("--page", type=int, default=1, help="목록 pageNum")
    args = ap.parse_args()

    list_url, list_params = build_list_url(args.community, args.page)

    try:
        html = fetch_html(list_url, params=list_params, referer=BASE)
    except Exception as e:
        print(f"[ERROR] 목록 요청 실패: {e}")
        sys.exit(1)

    items = parse_list(html)
    if not items:
        print("[WARN] 게시글 목록을 찾지 못했습니다.")
        # 디버깅 보조: 응답 일부 출력
        sample = html[:600].replace("\n", " ")
        print("[HINT] 응답 앞부분:", sample)
        sys.exit(2)

    print(f"[OK] 총 {len(items)}건 발견. 상위 {args.top}건:")
    for i, (title, href) in enumerate(items[:args.top], 1):
        abs_url = to_abs_view_url(href)
        print(f"{i:>2}. {title}\n    {abs_url}")

if __name__ == "__main__":
    main()
