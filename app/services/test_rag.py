from app.services.rag import RAGPipeline

rag = RAGPipeline()
question = "장기요양등급 판정 기준은 무엇인가요?"
response = rag.generate_answer(question)

print("GPT 응답:")
print(response)
