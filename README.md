# CareBridges AI Core
> **AI specialized in legal/labor/notification information for long-term care facility workers**
<br>

### [Upgraunder 1st Cohort - CareBridges] AI Repository
- This repository is a **RAG (Retrieval-Augmented Generation)** based LLM engine designed to provide senior care services and welfare information.
- It generates accurate information based on reliable data (public data, care guidelines, etc.) and provides personalized care consultations.
- Built with a high-performance API server based on **FastAPI**, **FAISS** vector search, and an automated deployment environment using **GitHub Actions + AWS CodeDeploy**.

---
## Tech Stack
### Language & Framework
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)

### LLM & RAG
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-4B8BBE?style=for-the-badge&logoColor=white)
![FAISS](https://img.shields.io/badge/FAISS-00599C?style=for-the-badge&logoColor=white)

### DevOps & Deployment
![AWS EC2](https://img.shields.io/badge/AWS_EC2-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![AWS CodeDeploy](https://img.shields.io/badge/AWS_CodeDeploy-6DB33F?style=for-the-badge&logo=amazonaws&logoColor=white)

### Technical Details
- **Language:** Python 3.10+
- **Framework:** FastAPI
- **LLM Model:** OpenAI GPT-4o
- **Vector DB:** FAISS (Facebook AI Similarity Search)
- **Deployment:** CI/CD pipeline based on AWS EC2 + GitHub Actions & AWS CodeDeploy
---

# 1. Project Structure and Key Source Code Description

Project Structure
```bash
carebridges-ai/
├── app/                    # FastAPI main service logic
│   ├── api/                # Endpoints and routing
│   │   └── endpoints/      # Core API logic (chat.py, retriever.py, etc.)
│   ├── core/               # Configuration management (config.py, dependencies.py)
│   ├── db/                 # Vector store management (vectorstore.py)
│   ├── schemas/            # Pydantic models (Request/Response specifications)
│   └── services/           # Business logic (chatbot.py, rag.py, openai_client.py)
├── crawler/                # Data collection pipeline
│   ├── notification.py     # Collection status notification module
│   ├── step2_build_manifest.py
│   ├── step3_download_convert.py
│   └── weekly_runner.py    # Weekly automated collection runner
├── data/                   # Initial data and FAQ repository
├── scripts/                # Server operation scripts (start.sh, stop.sh, etc.)
├── main.py                 # Service entry point
├── requirements.txt        # Dependency list
└── appspec.yml             # AWS CodeDeploy configuration file
```

Key Source Code Description

| Path | Description |
| --- | --- |
| **`main.py`** | Main entry point that runs the FastAPI application |
| **`app/services/chatbot.py`** | Passes user questions to GPT and generates responses matching the CareBridges persona |
| **`app/db/vectorstore.py`** | Embeds collected data and stores/loads it in FAISS vector DB (RAG knowledge base construction) |
| **`app/services/rag.py`** | Core RAG logic that embeds query sentences, searches for similar context in FAISS, and passes it to LLM |
| **`app/api/endpoints/chat.py`** | Receives questions via `/chat` route and returns answers as JSON after RAG process |
| **`crawler/weekly_runner.py`** | Execution script that regularly crawls new care/welfare information weekly to update data |
| **`app/core/config.py`** | Manages key environment variables such as OpenAI API key, AWS settings, FAISS index path |
| **`data/`** | Folder for storing crawled raw data and preprocessed text files |

---

# 2. How to Build and Install

### 1. Clone AI Repository
```bash
git clone https://github.com/carebridges-chatbot/carebridges-ai.git
cd carebridges-ai  # Navigate to the project after cloning
```

### 2. Set Up Virtual Environment (Optional)
```bash
python -m venv venv
source venv/bin/activate  # (For Windows: venv\Scripts\activate)
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables (.env)
Create a `.env` file in the project root directory and write environment variables in the following format:
```bash
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key

# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key

# Server Configuration
APP_ENV=development
PORT=8000
```
---

# 3. How to Test
The CareBridges AI server can be tested in two ways:
1. HTTP request testing using FastAPI Swagger UI
2. Interactive mode execution in terminal

The interactive mode allows faster and more convenient testing.
The server runs by default at `http://localhost:8000`.

---

# 4. Sample Data and Database Configuration
Sample Data Description
- The `data/` folder contains reliable public data text files such as senior welfare benefits and care guidelines.
- This data undergoes text chunking and embedding processing, vectorized so the AI can use it as a basis for answers.
- If data is manually modified, it must go through step 5 (Optional) initialization to be reflected.

---

# 5. Open Source Used
This project was developed based on the following open-source libraries:
- **LangChain**
  - Purpose: Building RAG (Retrieval-Augmented Generation) pipeline and managing LLM workflows
- **OpenAI API**
  - Purpose: High-performance natural language response generation and text embedding based on GPT-4o
- **FastAPI**
  - Purpose: High-performance REST API server implementation supporting asynchronous processing
- **FAISS**
  - Purpose: Efficient local vector storage and similarity search engine
- **BeautifulSoup4**
  - Purpose: Web data crawling for collecting latest welfare information
---

# CareBridges AI Core
> **AI specialized in legal/labor/notification information for long-term care facility workers**
<br>

### [업그라운더 1기 돌봄다리] AI 레포지토리입니다.
- 본 레포지토리는 시니어 케어 서비스 및 복지 정보를 제공하기 위해 고안된 **RAG(Retrieval-Augmented Generation)** 기반 LLM 엔진입니다.
- 신뢰할 수 있는 데이터(공공 데이터, 돌봄 가이드라인 등)를 바탕으로 정확한 정보를 생성하며, 사용자 맞춤형 돌봄 상담을 제공합니다.
- **FastAPI** 기반의 고성능 API 서버와 **FAISS** 벡터 검색, **GitHub Actions + AWS CodeDeploy** 기반의 자동 배포 환경을 구축하였습니다.

---
## 기술 스택
### Language & Framework
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)

### LLM & RAG
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-4B8BBE?style=for-the-badge&logoColor=white)
![FAISS](https://img.shields.io/badge/FAISS-00599C?style=for-the-badge&logoColor=white)

### DevOps & Deployment
![AWS EC2](https://img.shields.io/badge/AWS_EC2-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![AWS CodeDeploy](https://img.shields.io/badge/AWS_CodeDeploy-6DB33F?style=for-the-badge&logo=amazonaws&logoColor=white)

### 기술 디테일
- **Language:** Python 3.10+
- **Framework:** FastAPI
- **LLM Model:** OpenAI GPT-4o
- **Vector DB:** FAISS (Facebook AI Similarity Search)
- **Deployment:** AWS EC2 + GitHub Actions & AWS CodeDeploy 기반 CI/CD 파이프라인
---

# 1. 프로젝트 구조 및 주요 Source code 설명

프로젝트 구조
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
```
주요 Source code 설명

| 경로 | 설명 |
| --- | --- |
| **`main.py`** | FastAPI 애플리케이션을 실행하는 메인 진입점 |
| **`app/services/chatbot.py`** | 사용자의 질문을 GPT에게 전달하고, 케어브릿지 페르소나에 맞는 응답 생성 |
| **`app/db/vectorstore.py`** | 수집된 데이터를 임베딩하여 FAISS 벡터 DB에 저장 및 로드 (RAG 지식 베이스 구축) |
| **`app/services/rag.py`** | 쿼리 문장을 임베딩하고, FAISS에서 유사 문맥을 검색하여 LLM에 전달하는 RAG 핵심 로직 |
| **`app/api/endpoints/chat.py`** | `/chat` 라우트를 통해 질문을 수신하고, RAG 프로세스를 거친 답변을 JSON으로 반환 |
| **`crawler/weekly_runner.py`** | 매주 정기적으로 새로운 돌봄/복지 정보를 크롤링하여 데이터를 최신화하는 실행 스크립트 |
| **`app/core/config.py`** | OpenAI API 키, AWS 설정, FAISS 인덱스 경로 등 주요 환경 변수 관리 |
| **`data/`** | 크롤링된 원본 데이터 및 전처리된 텍스트 파일 저장 폴더 |

---

# 2. How to build and install

### 1. AI 레포지토리 Clone

```bash
git clone [https://github.com/carebridges-chatbot/carebridges-ai.git](https://github.com/carebridges-chatbot/carebridges-ai.git)
cd carebridges-ai  # 클론 후 해당 프로젝트로 이동
```
### 2. 가상환경 구성 (선택사항)
```bash
python -m venv venv
source venv/bin/activate  # (Windows의 경우: venv\Scripts\activate)
```
### 3. 의존성 설치
```bash
pip install -r requirements.txt
```
### 4. 환경 변수 설정 (.env)
프로젝트 루트 디렉토리에 `.env` 파일을 생성한 후, 아래와 같은 형식으로 환경 변수를 작성합니다:
```bash
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key

# AWS 설정
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key

# 서버 설정
APP_ENV=development
PORT=8000
```
---

# 3. How to test
케어브릿지 AI 서버는 두 가지 방식으로 테스트할 수 있습니다:
1. FastAPI Swagger UI를 이용한 HTTP 요청 테스트
2. 터미널에서 인터랙티브 모드 실행
이 중 인터랙티브 모드가 더 빠르고 편리하게 테스트할 수 있습니다.
서버는 기본적으로 `http://localhost:8000`에서 실행됩니다.

---
# 4. Sample Data 및 데이터베이스 구성
샘플 데이터 설명
- `data/` 폴더에는 시니어 복지 혜택, 돌봄 가이드라인 등 신뢰할 수 있는 공공 데이터 텍스트 파일이 포함됩니다.
- 이 데이터는 텍스트 청킹 과정을 거쳐 임베딩 처리되며, AI가 답변의 근거로 사용할 수 있도록 벡터화됩니다.
- 수동으로 데이터를 수정할 경우 5. (선택) 초기화 단계를 거쳐야 반영됩니다.

---
# 5. Open Source Used
본 프로젝트는 다음 오픈소스 라이브러리를 기반으로 개발되었습니다:
- LangChain
목적: RAG(검색 증강 생성) 파이프라인 구축 및 LLM 워크플로우 관리
- OpenAI API
목적: GPT-4o 기반 고성능 자연어 응답 생성 및 텍스트 임베딩
- FastAPI
목적: 비동기 처리를 지원하는 고성능 REST API 서버 구현
- FAISS
목적: 효율적인 로컬 벡터 저장 및 유사도 검색 엔진
- BeautifulSoup4
목적: 최신 복지 정보 수집을 위한 웹 데이터 크롤링









