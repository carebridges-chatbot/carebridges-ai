from typing import List

def build_prompt(documents: List[str], question: str) -> List[dict]:
    """
    검색 문서들과 사용자 질문을 받아 GPT 프롬프트(messages) 형식으로 변환
    """
    system_prompt = "너는 친절한 한국어 비서야. 주어진 문서 내용을 바탕으로 사용자 질문에 답변해."
    
    context = "\n\n".join(documents)
    user_prompt = f"다음 문서를 참고해서 질문에 답변해줘:\n\n{context}\n\n질문: {question}"

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
