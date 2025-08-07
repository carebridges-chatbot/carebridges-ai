from app.services.rag import RAGPipeline

class Chatbot:
    def __init__(self):
        self.pipeline = RAGPipeline()

    def chat(self, question: str) -> str:
        return self.pipeline.generate_answer(question)
