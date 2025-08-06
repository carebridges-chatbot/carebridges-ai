from vectorstore import VectorStoreHandler

def test_search():
    vs_handler = VectorStoreHandler(persist_path="db/faiss_index")
    vs_handler.load_vectorstore()
    
    results = vs_handler.search("치매 환자 돌봄 서비스", top_k=3)
    for i, doc in enumerate(results, 1):
        print(f"\n[{i}] {doc.page_content[:200]}...")  # 내용 일부 출력

if __name__ == "__main__":
    test_search()
