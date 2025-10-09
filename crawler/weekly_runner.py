# -*- coding: utf-8 -*-
"""
Step 0: Weekly Runner (월요일 03:00 KST)
- --once  : 즉시 1회 실행
- --daemon: 매주 월요일 03:00 KST에 순차 실행 (무한루프 대기)
실행 순서:
  1) step2_build_manifest.py  (신규만 선별)
  2) step3_download_convert.py  (있으면 실행; 없으면 건너뜀)
  3) step4_upload.py            (있으면 실행; 없으면 건너뜀)

사용방법
    # 1) 즉시 1회 테스트 실행
    python -m crawler.weekly_runner --once --top 10

    # 2) 데몬 모드(주 1회 월요일 03:00 자동)
    python -m crawler.weekly_runner --daemon --top 10

"""
from __future__ import annotations
import argparse, subprocess, sys, time, importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORK = ROOT / "_work"
MANIFEST = WORK / "manifest.json"

def run_step(mod: str, args: list[str] | None = None) -> int:
    cmd = [sys.executable, "-m", f"crawler.{mod}"]
    if args:
        cmd += args
    print(f"[RUN] {' '.join(cmd)}")
    return subprocess.call(cmd)

def exists_module(mod: str) -> bool:
    return importlib.util.find_spec(f"crawler.{mod}") is not None

def one_cycle(top: int = 10, community: str = "B0018") -> None:
    print(f"[CYCLE] start: top={top}, community={community}")

    # Step 2: 신규만 선별 (매니페스트 생성)
    code = run_step("step2_build_manifest", ["--top", str(top), "--community", community])
    if code != 0:
        print(f"[ERROR] step2_build_manifest failed with code {code}")
        return

    if not MANIFEST.exists() or MANIFEST.stat().st_size == 0:
        print("[INFO] manifest.json 없음 또는 비어 있음 → 처리할 신규 없음. 종료")
        return

    # Step 3: 다운로드·변환 (있을 때만)
    if exists_module("step3_download_convert"):
        code = run_step("step3_download_convert")
        if code != 0:
            print(f"[ERROR] step3_download_convert failed with code {code}")
            return
    else:
        print("[SKIP] step3_download_convert.py 없음 → 다음 단계로")

    # Step 4: 업로드 (있을 때만)
    if exists_module("step4_upload"):
        code = run_step("step4_upload")
        if code != 0:
            print(f"[ERROR] step4_upload failed with code {code}")
            return
    else:
        print("[SKIP] step4_upload.py 없음 → 파이프라인 종료")

    print("[CYCLE] complete.")
    
    # 알림 전송
    try:
        from crawler.notification import create_pipeline_summary, send_pipeline_notification
        upload_results_path = ROOT / "_work" / "upload_results.json"
        if upload_results_path.exists():
            summary = create_pipeline_summary(upload_results_path)
            send_pipeline_notification(summary)
            print("[NOTIFICATION] 알림 전송 완료")
    except Exception as e:
        print(f"[WARN] 알림 전송 실패: {e}")

def sleep_until_next_monday_3am_kst() -> None:
    # Python 3.10: zoneinfo 사용
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo("Asia/Seoul")
    except Exception:
        tz = None

    from datetime import datetime, timedelta, time as dtime

    def now_kst():
        return datetime.now(tz) if tz else datetime.utcnow() + timedelta(hours=9)

    now = now_kst()
    # Monday=0 ... Sunday=6
    weekday = now.weekday()
    target = now

    # 다음 월요일 03:00 계산
    # 오늘이 월요일이고 03:00 이전이면 오늘 03:00, 아니면 다음 월요일 03:00
    if weekday == 0 and (now.hour, now.minute) < (3, 0):
        target = now.replace(hour=3, minute=0, second=0, microsecond=0)
    else:
        days_ahead = (7 - weekday) % 7
        if days_ahead == 0:
            days_ahead = 7
        target_date = (now + timedelta(days=days_ahead)).date()
        target = (datetime.combine(target_date, dtime(3, 0)) if not tz
                  else datetime.combine(target_date, dtime(3, 0), tzinfo=tz))

    secs = max(0, int((target - now).total_seconds()))
    print(f"[SCHED] 다음 실행: {target.isoformat()} (대기 {secs}초)")
    time.sleep(secs)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", help="즉시 1회 실행")
    ap.add_argument("--daemon", action="store_true", help="매주 월요일 03:00 KST 자동 실행")
    ap.add_argument("--top", type=int, default=10, help="Step2에 넘길 상위 개수")
    ap.add_argument("--community", default="B0018", help="게시판 communityKey")
    args = ap.parse_args()

    if args.once and args.daemon:
        print("[ERROR] --once와 --daemon은 같이 쓸 수 없습니다.")
        sys.exit(2)

    if args.once:
        one_cycle(top=args.top, community=args.community)
        return

    if args.daemon:
        print("[MODE] daemon (weekly Monday 03:00 KST)")
        while True:
            sleep_until_next_monday_3am_kst()
            try:
                one_cycle(top=args.top, community=args.community)
            except Exception as e:
                print(f"[FATAL] pipeline error: {e}")
        # 루프는 끊지 않습니다.

    # 기본은 한번 실행
    one_cycle(top=args.top, community=args.community)

if __name__ == "__main__":
    main()