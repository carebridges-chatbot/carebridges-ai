from app.services.rag import RAGPipeline

rag = RAGPipeline()
question = "서비스 인정점수 하향 조정됐다는데 어떻게 바뀌었나요?"
response = rag.generate_answer(question)

print("GPT 응답:")
print(response)
