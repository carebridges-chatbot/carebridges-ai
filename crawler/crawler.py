# -*- coding: utf-8 -*-
"""
Crawler (단일 파일)
- 목록:  /npbs/cms/board/board/Board.jsp?act=LIST&communityKey=...
- 상세:  /npbs/cms/board/board/Board.jsp?act=VIEW&boardId=...
- 기능:
  1) 공지/일반글을 구분해 목록 파싱 (공지 전부 포함, 일반글은 boardId 기준 중복 제거)
  2) 상위 N건에 대해 상세 페이지에서 첨부파일(.pdf/.hwp/.hwpx 또는 Download.jsp) 링크 추출
- 출력: 제목, 상세 URL, 첨부 URL들
"""

from __future__ import annotations
import sys
import argparse
import re
from typing import List, Tuple
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

BASE = "https://www.longtermcare.or.kr"
LIST_PATH = "/npbs/cms/board/board/Board.jsp"
VIEW_PATH = "/npbs/cms/board/board/Board.jsp"  # act=VIEW 동일

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

def build_list_url(community_key: str = "B0018", page_num: int = 1) -> Tuple[str, dict]:
    url = BASE + LIST_PATH
    params = {
        "act": "LIST",
        "communityKey": community_key,
        "pageNum": str(page_num),
        "searchType": "ALL",
        "searchWord": "",
        "list_start_date": "",
        "list_end_date": "",
        "pageSize": "",
        "list_show_answer": "N",
        "branch_id": "",
        "branch_child_id": "",
    }
    return url, params

def parse_list(html: str) -> List[Tuple[str, str]]:
    """
    공지/일반글을 구분해서 (제목, a[href]) 반환.
    - 공지: <td headers="board_num"> 내부에 <span class="noti">공지</span>
    - 일반글: boardId=숫자 기준으로 중복 제거
    - 최종 결과: 공지들 + 일반글들 (화면 순서와 동일하게 가까운 순서)
    """
    soup = BeautifulSoup(html, "lxml")

    # 테이블의 모든 행 탐색
    rows = soup.select("table tr")
    notices: List[Tuple[str, str]] = []
    normals: List[Tuple[str, str]] = []
    seen_ids = set()

    for tr in rows:
        td_title = tr.find("td", attrs={"headers": re.compile(r"\bboard_title\b", re.I)})
        if not td_title:
            continue
        a = td_title.find("a")
        if not a:
            continue

        title = (a.get_text(separator=" ", strip=True) or "").replace("\xa0", " ").strip()
        href = (a.get("href") or "").strip()
        if not href:
            continue

        m = re.search(r"[?&]boardId=(\d+)", href)
        if not m:
            # boardId가 없으면 상세 진입 불가라 스킵
            continue
        board_id = m.group(1)

        # 공지 여부
        td_num = tr.find("td", attrs={"headers": re.compile(r"\bboard_num\b", re.I)})
        is_notice = td_num is not None and td_num.find("span", class_="noti") is not None

        if is_notice:
            # 공지는 전부 포함 (중복이라도 그대로 둠: 공지 영역이 별도여서 의도적으로 모두 보존)
            notices.append((title, href))
        else:
            # 일반글은 boardId 기준으로 중복 제거
            if board_id in seen_ids:
                continue
            seen_ids.add(board_id)
            normals.append((title, href))

    # 화면 상단의 공지들을 먼저, 그 다음 일반글
    return notices + normals

def to_abs_view_url(href: str) -> str:
    """목록 a[href]를 절대 상세 URL로 변환"""
    if href.lower().startswith("http"):
        return href
    if href.startswith("?"):
        return BASE + VIEW_PATH + href
    return urljoin(BASE + VIEW_PATH, href)

def extract_attachments_from_view(html: str, base_url: str) -> List[str]:
    """
    상세 페이지에서 첨부파일 링크 수집:
    - a[href]에 .pdf/.hwp/.hwpx 포함
    - a[href]에 'Download.jsp' 또는 'download' 포함
    - 첨부 아이콘(img alt에 '첨부'/'파일') 주변 a[href]
    """
    soup = BeautifulSoup(html, "lxml")

    def is_file_href(h: str) -> bool:
        h_low = h.lower()
        return (
            (".pdf" in h_low)
            or (".hwp" in h_low)
            or (".hwpx" in h_low)
            or ("download.jsp" in h_low)
            or ("download" in h_low)
        )

    urls: List[str] = []

    # (1) 확장자/키워드 기반
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href and is_file_href(href):
            urls.append(urljoin(base_url, href))

    # (2) 첨부 아이콘 주변
    icons = soup.find_all("img", alt=re.compile(r"첨부|파일", re.I))
    for icon in icons:
        parent = icon.parent
        if not parent:
            continue
        for a in parent.find_all("a", href=True):
            href = a["href"].strip()
            if href:
                urls.append(urljoin(base_url, href))

    # 중복 제거(순서 유지)
    seen = set()
    uniq = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--community", default="B0018", help="communityKey (기본: 법령자료실 B0018)")
    ap.add_argument("--page", type=int, default=1, help="목록 pageNum")
    ap.add_argument(
        "--top", type=int, default=10,
        help="상위 몇 개 상세 페이지만 처리 (공지 포함 권장: 10)"
    )
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
        sample = html[:600].replace("\n", " ")
        print("[HINT] 응답 앞부분:", sample)
        sys.exit(2)

    print(f"[OK] 총 {len(items)}건. 상위 {args.top}건(공지 전부 포함, 일반글 dedup) 첨부 탐색:\n")

    for i, (title, href) in enumerate(items[:args.top], 1):
        view_url = to_abs_view_url(href)
        try:
            view_html = fetch_html(view_url, referer=list_url)
        except Exception as e:
            print(f"{i:>2}. {title}\n    [ERROR] 상세 요청 실패: {e}\n")
            continue

        attach_urls = extract_attachments_from_view(view_html, view_url)

        print(f"{i:>2}. {title}\n    상세: {view_url}")
        if attach_urls:
            for j, u in enumerate(attach_urls, 1):
                print(f"    첨부{j}: {u}")
        else:
            print("    첨부: (없음/탐지 실패)")
        print()

if __name__ == "__main__":
    main()