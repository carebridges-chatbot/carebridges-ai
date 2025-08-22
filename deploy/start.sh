#!/bin/bash

# 애플리케이션을 시작하는 명령어
echo "Starting the Flask application using systemd..."
sudo systemctl start carebridegs # systemd 서비스 실행
echo "Flask application started."