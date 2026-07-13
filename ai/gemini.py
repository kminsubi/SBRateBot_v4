import os
import ssl

# 회사망 SSL 인증서 문제 대응
ssl._create_default_https_context = ssl._create_unverified_context


from google import genai



client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)



def ask_gemini(question, data):


    prompt = f"""
당신은 저축은행 수신금리 전문 AI입니다.

아래 금리 데이터를 참고하여 사용자의 질문에 답변하세요.


[금리 데이터]

{data}



[사용자 질문]

{question}



답변 규칙

1. 숫자는 % 단위로 표시
2. 필요한 경우 순위를 계산
3. 비교 질문이면 비교 결과 제시
4. 이유와 시장 배경을 설명
5. 금융 전문가처럼 자연스럽게 답변
6. 단순 나열보다 분석 의견 포함
"""



    try:


        response = client.models.generate_content(

            model="gemini-2.5-flash",

            contents=prompt

        )


        return response.text



    except Exception as e:


        return f"Gemini 오류 : {e}"