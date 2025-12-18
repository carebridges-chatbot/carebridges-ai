# 🌉 CareBridges AI Core
> **돌봄의 사각지대를 기술로 잇다, RAG 기반 지능형 시니어 케어 챗봇 엔진**
<br>

### 🎙️ [업그라운더 1기 돌봄다리] AI 레포지토리입니다.
- 본 레포지토리는 시니어 케어 서비스 및 복지 정보를 제공하기 위해 고안된 **RAG(Retrieval-Augmented Generation)** 기반 LLM 엔진입니다.
- 신뢰할 수 있는 데이터(공공 데이터, 돌봄 가이드라인 등)를 바탕으로 정확한 정보를 생성하며, 사용자 맞춤형 돌봄 상담을 제공합니다.
- **FastAPI** 기반의 고성능 API 서버와 **FAISS** 벡터 검색, **GitHub Actions + AWS CodeDeploy** 기반의 자동 배포 환경을 구축하였습니다.

---
## 🔧 기술 스택
### 📌 Language & Framework
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)

### 📌 LLM & RAG
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-4B8BBE?style=for-the-badge&logoColor=white)
![FAISS](https://img.shields.io/badge/FAISS-00599C?style=for-the-badge&logoColor=white)

### 📌 DevOps & Deployment
![AWS EC2](https://img.shields.io/badge/AWS_EC2-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![AWS CodeDeploy](https://img.shields.io/badge/AWS_CodeDeploy-6DB33F?style=for-the-badge&logo=amazonaws&logoColor=white)

### 🔎 기술 디테일
- **Language:** Python 3.10+
- **Framework:** FastAPI
- **LLM Model:** OpenAI GPT-4o
- **Vector DB:** FAISS (Facebook AI Similarity Search)
- **Deployment:** AWS EC2 + GitHub Actions & AWS CodeDeploy 기반 CI/CD 파이프라인
---

# 1. 프로젝트 구조 및 주요 Source code 설명

📁 프로젝트 구조
```bash
carebridges-ai/
├── app/                    # FastAPI 메인 서비스 로직
│   ├── api/                # 엔드포인트 및 라우팅
│   │   └── endpoints/      # chat.py, retriever.py 등 핵심 API 로직
│   ├── core/               # 설정 관리 (config.py, dependencies.py)
│   ├── db/                 # 벡터 스토어 관리 (vectorstore.py)
│   ├── schemas/            # Pydantic 모델 (Request/Response 규격)
│   └── services/           # 비즈니스 로직 (chatbot.py, rag.py, openai_client.py)
├── crawler/                # 데이터 수집 파이프라인
│   ├── notification.py     # 수집 상태 알림 모듈
│   ├── step2_build_manifest.py
│   ├── step3_download_convert.py
│   └── weekly_runner.py    # 주간 단위 자동 수집 실행기
├── data/                   # 초기 데이터 및 FAQ 저장소
├── scripts/                # 서버 운용 스크립트 (start.sh, stop.sh 등)
├── main.py                 # 서비스 진입점
├── requirements.txt        # 의존성 목록
└── appspec.yml             # AWS CodeDeploy 설정 파일
