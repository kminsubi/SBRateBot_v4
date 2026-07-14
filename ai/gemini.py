import os
import ssl

from dotenv import load_dotenv
from google import genai


# ===================================
# SBRateBot V4 Gemini 설정
# ===================================


# 프로젝트 루트 위치
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# .env 위치
ENV_PATH = os.path.join(
    BASE_DIR,
    ".env"
)


# 환경변수 로드
load_dotenv(
    ENV_PATH
)


# ===================================
# 회사망 SSL 인증서 문제 우회
# ===================================

ssl._create_default_https_context = (
    ssl._create_unverified_context
)


# ===================================
# Gemini API Client
# ===================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)


if not GEMINI_API_KEY:

    raise ValueError(
        "GEMINI_API_KEY가 없습니다. "
        ".env 파일을 확인하세요."
    )



client = genai.Client(
    api_key=GEMINI_API_KEY
)



# ===================================
# Gemini AI 질문
# ===================================


def ask_gemini(
    question,
    data
):


    prompt = f"""

저축은행 수신금리 전문 AI입니다.

아래 금리 데이터를 기반으로 사용자의 질문에 답변하세요.


[금리 데이터]

{data}



[사용자 질문]

{question}



답변 기준

1. 금리는 % 단위로 표시
2. 필요한 경우 순위 계산
3. 비교 질문은 비교 결과 제공
4. 금리 차이는 %p 기준 표시
5. 시장 상황과 배경 설명
6. 금융 전문가 관점으로 답변
7. 단순 나열보다 분석 포함

"""


    try:


        response = client.models.generate_content(

            model="gemini-3.1-flash-lite",

            contents=prompt

        )


        return response.text



    except Exception as e:


        return (
            "Gemini 응답 오류 : "
            + str(e)
        )