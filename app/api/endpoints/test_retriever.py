import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))


from retriever import Retriever

retriever = Retriever()
docs = retriever.retrieve("노인 장기요양 등급 신청 방법 알려줘", top_k=3)

for i, doc in enumerate(docs, 1):
    print(f"\n[{i}] {doc.page_content[:500]}...")
