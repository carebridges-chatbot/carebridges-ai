# -*- coding: utf-8 -*-
"""
알림 시스템
- Discord 웹훅 알림
- 이메일 알림 (SMTP)
- 파이프라인 실행 결과 알림
"""
from __future__ import annotations
import json, os, smtplib, requests
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_discord_notification(webhook_url: str, title: str, message: str, color: int = 0x00ff00) -> bool:
    """Discord 웹훅으로 알림 전송"""
    try:
        embed = {
            "title": title,
            "description": message,
            "color": color,
            "timestamp": datetime.now().isoformat(),
            "footer": {
                "text": "CareBridges 문서 크롤링 파이프라인"
            }
        }
        
        payload = {
            "embeds": [embed]
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        
        print(f"[DISCORD] 알림 전송 성공: {title}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Discord 알림 실패: {e}")
        return False

def send_email_notification(smtp_config: Dict[str, str], to_email: str, subject: str, body: str) -> bool:
    """이메일로 알림 전송"""
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_config['from_email']
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        
        server = smtplib.SMTP(smtp_config['smtp_server'], smtp_config['smtp_port'])
        server.starttls()
        server.login(smtp_config['username'], smtp_config['password'])
        
        text = msg.as_string()
        server.sendmail(smtp_config['from_email'], to_email, text)
        server.quit()
        
        print(f"[EMAIL] 알림 전송 성공: {to_email}")
        return True
        
    except Exception as e:
        print(f"[ERROR] 이메일 알림 실패: {e}")
        return False

def create_pipeline_summary(upload_results_path: Path) -> Dict[str, Any]:
    """파이프라인 실행 결과 요약 생성"""
    if not upload_results_path.exists():
        return {
            "status": "failed",
            "message": "업로드 결과 파일이 없습니다.",
            "total_files": 0,
            "success_files": 0,
            "failed_files": 0
        }
    
    with open(upload_results_path, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    total_files = sum(len(item['files']) for item in results)
    success_files = sum(1 for item in results for f in item['files'] if f['status'] == 'success')
    failed_files = total_files - success_files
    
    return {
        "status": "success" if failed_files == 0 else "partial",
        "total_posts": len(results),
        "total_files": total_files,
        "success_files": success_files,
        "failed_files": failed_files,
        "results": results
    }

def send_pipeline_notification(summary: Dict[str, Any]) -> None:
    """파이프라인 실행 결과 알림 전송"""
    
    # Discord 알림
    discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
    if discord_webhook:
        if summary['status'] == 'success':
            title = "✅ 문서 크롤링 완료"
            message = f"📊 **처리 결과**\n• 게시물: {summary['total_posts']}개\n• 파일: {summary['success_files']}개 업로드 성공"
            color = 0x00ff00  # 초록색
        elif summary['status'] == 'partial':
            title = "⚠️ 문서 크롤링 부분 완료"
            message = f"📊 **처리 결과**\n• 게시물: {summary['total_posts']}개\n• 성공: {summary['success_files']}개\n• 실패: {summary['failed_files']}개"
            color = 0xffaa00  # 주황색
        else:
            title = "❌ 문서 크롤링 실패"
            message = f"📊 **처리 결과**\n• {summary['message']}"
            color = 0xff0000  # 빨간색
        
        send_discord_notification(discord_webhook, title, message, color)
    
    # 이메일 알림
    smtp_config = {
        'smtp_server': os.getenv('SMTP_SERVER'),
        'smtp_port': int(os.getenv('SMTP_PORT', '587')),
        'username': os.getenv('SMTP_USERNAME'),
        'password': os.getenv('SMTP_PASSWORD'),
        'from_email': os.getenv('SMTP_FROM_EMAIL')
    }
    
    to_email = os.getenv('NOTIFICATION_EMAIL')
    if all(smtp_config.values()) and to_email:
        if summary['status'] == 'success':
            subject = "✅ CareBridges 문서 크롤링 완료"
            body = f"""
            <h2>📊 문서 크롤링 완료</h2>
            <p><strong>처리 결과:</strong></p>
            <ul>
                <li>게시물: {summary['total_posts']}개</li>
                <li>파일: {summary['success_files']}개 업로드 성공</li>
            </ul>
            <p>모든 파일이 성공적으로 처리되었습니다.</p>
            """
        elif summary['status'] == 'partial':
            subject = "⚠️ CareBridges 문서 크롤링 부분 완료"
            body = f"""
            <h2>📊 문서 크롤링 부분 완료</h2>
            <p><strong>처리 결과:</strong></p>
            <ul>
                <li>게시물: {summary['total_posts']}개</li>
                <li>성공: {summary['success_files']}개</li>
                <li>실패: {summary['failed_files']}개</li>
            </ul>
            <p>일부 파일 처리에 실패했습니다. 로그를 확인해주세요.</p>
            """
        else:
            subject = "❌ CareBridges 문서 크롤링 실패"
            body = f"""
            <h2>📊 문서 크롤링 실패</h2>
            <p><strong>오류:</strong> {summary['message']}</p>
            <p>파이프라인 실행에 실패했습니다. 로그를 확인해주세요.</p>
            """
        
        send_email_notification(smtp_config, to_email, subject, body)

def main():
    """알림 테스트"""
    import argparse
    
    ap = argparse.ArgumentParser()
    ap.add_argument("--upload-results", default="_work/upload_results.json", help="업로드 결과 파일")
    args = ap.parse_args()
    
    # 파이프라인 결과 요약
    summary = create_pipeline_summary(Path(args.upload_results))
    
    # 알림 전송
    send_pipeline_notification(summary)
    
    print(f"[NOTIFICATION] 알림 전송 완료: {summary['status']}")

if __name__ == "__main__":
    main()