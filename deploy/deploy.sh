#!/bin/bash

echo "Starting deployment process..."

#  기존 서비스 중지
echo "Stopping the current Flask application..."
./deploy/stop.sh

#  최신 코드 가져오기
echo "Pulling the latest code from Git..."

#  가상환경 활성화 및 패키지 설치 (필요할 경우)
echo "Installing dependencies..."

#배포된 디렉터리로 이동
cd /home/ubuntu/carebridges-rag

# 가상환경 경로 지정
VENV="/home/ubuntu/carebridges-rag/cb-rag-venv"
REQ="/home/ubuntu/carebridges-rag/requirements.txt"

# 가상환경이 없으면 생성
if [ ! -d "$VENV" ]; then
    echo "Virtual environment not found! Creating venv..."
    python3 -m venv "$VENV"
fi

# 가상환경 활성화 및 패키지 설치
echo "Activating virtual environment..."
source "$VENV/bin/activate"

python -m pip install --upgrade pip
pip install -r "$REQ"


# 서비스 파일 복사
echo "Copying the carebridges.service file..."
cp /home/ubuntu/carebridges-rag/carebridges.service /etc/systemd/system/

# systemd 리로드
echo "Reloading systemd daemon..."
systemctl daemon-reload

# 서비스 시작
echo "Starting the carebridges service..."
systemctl start carebridges.service

# 서비스가 부팅 시 자동으로 시작되도록 설정
systemctl enable carebridges.service

# 개발 서비스 재시작
systemctl restart carebridges-dev.service
systemctl enable carebridges-dev.service

#  Flask 애플리케이션 재시작
echo "Restarting the Flask application..."
./scripts/start.sh

echo "Deployment completed!"