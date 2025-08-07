from openai_clinet import OpenAIClient
from dotenv import load_dotenv
load_dotenv()

def test_openai_client():
    client = OpenAIClient()
    messages = [
        {"role": "system", "content": "너는 친절한 한국어 도우미야."},
        {"role": "user", "content": "GPT-4o-mini는 뭐야?"}
    ]

    response = client.chat(messages)
    print("GPT 응답:", response)

if __name__ == "__main__":
    test_openai_client()
