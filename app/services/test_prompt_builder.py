from app.db.vectorstore import VectorStoreHandler
from app.services.prompt_builder import build_prompt
from app.services.openai_client import OpenAIClient

# 1. 벡터스토어 로드
vectorstore = VectorStoreHandler()
vectorstore.load_vectorstore()

# 2. 사용자 질문
question = "장기요양등급 판정 기준은 무엇인가요?"

# 3. 관련 문서 검색 (예: 상위 5개)
retrieved_docs = vectorstore.search(query=question, top_k=5)

# 4. 문서 내용을 추출해서 리스트로 변환
doc_texts = [doc.page_content for doc in retrieved_docs]

# 5. 프롬프트 생성
messages = build_prompt(doc_texts, question)

# 6. GPT 호출
client = OpenAIClient()
response = client.chat(messages)

# 7. 결과 출력
print("\nGPT 응답:")
print(response)
