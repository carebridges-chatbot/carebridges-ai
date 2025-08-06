from split_documents import split_pdf

def main():
    file_path = "data\제1장_장기요양인정_신청.pdf (248037 Bytes)"  # PDF 경로
    chunks = split_pdf(file_path)

    print(f"\n총 {len(chunks)}개의 청크로 분할됨.")

    # 앞 3개 청크만 출력
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- Chunk {i+1} ---")
        print(chunk.page_content[:300])  # 앞 300자만 출력

if __name__ == "__main__":
    main()
