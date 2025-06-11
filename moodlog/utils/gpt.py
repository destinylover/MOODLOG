from openai import OpenAI
from openai.types.chat import ChatCompletionMessage
import os
from dotenv import load_dotenv
import json

# 환경변수에서 API 키 로드
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# 클라이언트 초기화
client = OpenAI(api_key=api_key)

def analyze_diary_emotion(diary: str) -> dict:
    """
    일기 내용을 받아 감정 분석 결과를 반환한다.
    결과는 emotion, advice, score를 포함하는 딕셔너리이다.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "일기에서 감정을 분석하고 아래 JSON 포맷으로 응답하세요. {\"emotion\": \"감정\", \"advice\": \"조언\", \"score\": 숫자}"
            },
            {
                "role": "user",
                "content": diary
            }
        ],
        temperature=0.7
    )

    content = response.choices[0].message.content.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # JSON 파싱 실패 시, 기본 형식으로 반환
        return {
            "emotion": "분석 불가",
            "advice": content,
            "score": 0.5
        }
