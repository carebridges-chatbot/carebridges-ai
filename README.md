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
📁 주요 Source code 설명경로설명app/services/rag.pyRAG 아키텍처의 핵심 로직 (검색 및 증강 생성 통합 제어)app/services/chatbot.py시스템 프롬프트 관리 및 대화 컨텍스트 처리app/api/endpoints/retriever.py입력된 쿼리에 대해 벡터 DB(FAISS)에서 관련 문서를 검색하는 모듈crawler/weekly_runner.py주기적으로 최신 복지 정보를 수집하여 데이터베이스를 최신화하는 파이프라인app/core/config.pyAPI 키 및 AWS 설정값 등 환경 변수 관리2. How to build and install1. AI 레포지토리 CloneBashgit clone [https://github.com/carebridges-chatbot/carebridges-ai.git](https://github.com/carebridges-chatbot/carebridges-ai.git)
cd carebridges-ai
2. 가상환경 구성 및 의존성 설치Bashpython -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
3. 환경 변수 설정 (.env)루트 디렉토리에 .env 파일을 생성하고 아래 형식을 참조하여 작성합니다.코드 스니펫OPENAI_API_KEY=your_key_here
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
# 기타 서비스 설정값들...
3. How to test방법 1. FastAPI Swagger UI (추천)서버를 실행한 후 브라우저에서 인터랙티브하게 API를 테스트할 수 있습니다.Bashuvicorn main:app --reload
URL: http://localhost:8000/docs 접속방법 2. Crawler 테스트데이터 수집 파이프라인이 정상 작동하는지 확인하려면 아래 명령어를 실행합니다.Bashpython crawler/weekly_runner.py
4. 데이터베이스 및 RAG 구성🗃️ Vector DB: FAISS사용 목적: 방대한 복지 정책 및 돌봄 가이드라인 중 질문과 가장 관련 있는 문서 추출인덱스 위치: db/faiss_index프로세스:crawler/를 통해 데이터 수집app/db/vectorstore.py를 통해 임베딩 및 인덱싱질문 발생 시 유사도 기반 검색 후 LLM 전달5. Open Source UsedLangChain: LLM 체인 및 RAG 워크플로우 관리FastAPI: 비동기 기반 고성능 API 서버OpenAI SDK: GPT-4o 연동FAISS: 효율적인 벡터 검색 엔진✏️ SW 구조도(여기에 나중에 이미지 업로드 후 링크를 넣으세요!)
