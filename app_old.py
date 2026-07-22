# ===================================
# SBRateBot V4 app.py 수정본
# 1/4
# ===================================


from flask import Flask, render_template, jsonify, request

from ai.gemini import ask_gemini, market_summary

import json
import os
import re


app = Flask(__name__)


# -------------------------------
# 기본 경로 설정
# -------------------------------

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


DATA_FILE = os.path.join(
    BASE_DIR,
    "data",
    "latest_rates.json"
)


# -------------------------------
# 기간 설정
# -------------------------------

PERIOD_MAP = {

    "1개월": "1",
    "3개월": "3",
    "6개월": "6",
    "12개월": "12",
    "24개월": "24",
    "36개월": "36"

}


FINANCIAL_BANKS = [

    "우리금융저축은행",
    "신한저축은행",
    "하나저축은행",
    "KB저축은행"

]


# -------------------------------
# 데이터 로드
# -------------------------------

def load_rates():

    try:

        with open(

            DATA_FILE,

            "r",

            encoding="utf-8"

        ) as f:

            data = json.load(f)


        if isinstance(data, list):

            return [

                x

                for x in data

                if isinstance(x, dict)

            ]


        if isinstance(data, dict):

            return data.get(
                "REC",
                []
            )


        return []


    except Exception as e:

        print(
            "DATA LOAD ERROR:",
            e
        )

        return []



# -------------------------------
# 숫자 변환
# -------------------------------

def safe_float(value):

    try:

        if value in [

            None,
            "",
            "-"

        ]:

            return None


        return float(

            str(value).replace(
                ",",
                ""
            )

        )


    except Exception:

        return None



# -------------------------------
# 문자열 정규화
# -------------------------------

def normalize(text):


    text = str(text or "")



    replace_list = [

        "(주)",

        "㈜",

        "주식회사",

        "저축은행",

        "은행",

        " ",

        "-"

    ]



    for item in replace_list:


        text = text.replace(

            item,

            ""

        )


    return text.lower()



# -------------------------------
# 상품 데이터 생성
# -------------------------------

def build_products(
    period_name="12개월"
):

    raw_data = load_rates()


    period = PERIOD_MAP.get(

        period_name,

        "12"

    )


    rate_field = (

        "top_"

        +

        period

        +

        "m"

    )


    change_field = (

        "change_"

        +

        period

    )


    products = []


    for item in raw_data:


        rate = safe_float(

            item.get(
                rate_field
            )

        )


        if rate is None:

            rate = 0



        change = safe_float(

            item.get(
                change_field
            )

        )


        if change is None:

            change = 0



        bank = str(

            item.get(
                "bank",
                ""
            )

            or ""

        ).strip()



        product = str(

            item.get(
                "product",
                ""
            )

            or ""

        ).strip()



        if not bank or not product:

            continue



        products.append({

            "category":
                "정기예금",

            "period":
                period_name,

            "bank":
                bank,

            "product":
                product,

            "rate":
                rate,

            "change":
                change,

            "reg_date":
                item.get(
                    "reg_date",
                    ""
                )

        })


    return products



# -------------------------------
# 중복 제거
# -------------------------------

def unique_products(products):

    result = []

    seen = set()


    for item in products:


        key = (

            item["bank"],

            item["product"],

            item["period"]

        )


        if key in seen:

            continue


        seen.add(key)

        result.append(item)


    return result



# -------------------------------
# 은행 상품 검색
# -------------------------------

def find_bank_products(

    products,

    keyword

):


    keyword = normalize(keyword)


    result = []



    for item in products:


        bank_name = normalize(

            item["bank"]

        )


        if keyword in bank_name:


            result.append(item)



    return result
    
    # ===================================
# SBRateBot V4 app.py 수정본
# 2/4
# ===================================


# -------------------------------
# 은행별 최고 금리
# -------------------------------

def get_bank_best_rates(products):

    bank_map = {}


    for item in products:

        bank = item["bank"]


        if (

            bank not in bank_map

            or

            item["rate"]

            >

            bank_map[bank]["rate"]

        ):

            bank_map[bank] = item



    return list(

        bank_map.values()

    )



# -------------------------------
# 시장 순위 계산
# -------------------------------

def get_market_bank_rank(
    products,
    target_bank
):

    bank_best = get_bank_best_rates(
        products
    )


    bank_best = [

        x

        for x in bank_best

        if x["rate"] > 0

    ]



    bank_best.sort(

        key=lambda x:

        x["rate"],

        reverse=True

    )



    rank = "-"


    target = normalize(
        target_bank
    )


    for idx,item in enumerate(

        bank_best,

        start=1

    ):


        if normalize(item["bank"]) == target:

            rank = idx

            break



    return {

        "rank":
            rank,

        "total":
            len(bank_best)

    }




# -------------------------------
# 메인 페이지
# -------------------------------

@app.route("/")

def index():

    return render_template(
        "index.html"
    )




# -------------------------------
# KPI API
# -------------------------------

@app.route("/api/kpi")

def api_kpi():


    products = unique_products(

        build_products(
            "12개월"
        )

    )


    products = [

        x

        for x in products

        if x["rate"] > 0

    ]



    if not products:

        return jsonify({

            "product_count":
                0,

            "max_rate":
                "0.00%",

            "average_rate":
                "0.00%",

            "min_rate":
                "0.00%"

        })



    max_rate = max(

        x["rate"]

        for x in products

    )



    min_rate = min(

        x["rate"]

        for x in products

    )



    avg = sum(

        x["rate"]

        for x in products

    ) / len(products)



    return jsonify({

        "product_count":

            len(products),


        "max_rate":

            f"{max_rate:.2f}%",


        "average_rate":

            f"{avg:.2f}%",


        "min_rate":

            f"{min_rate:.2f}%"

    })




# -------------------------------
# 우리금융 Market Position
# -------------------------------

@app.route("/api/woori")

def api_woori():


    products = unique_products(

        build_products(
            "12개월"
        )

    )


    products = [

        x

        for x in products

        if x["rate"] > 0

    ]



    woori_products = find_bank_products(

        products,

        "우리금융저축은행"

    )



    if not woori_products:

        return jsonify({

            "bank":

                "우리금융저축은행"

        })



    woori = max(

        woori_products,

        key=lambda x:

        x["rate"]

    )



    rank = get_market_bank_rank(

        products,

        woori["bank"]

    )



    avg = sum(

        x["rate"]

        for x in products

    ) / len(products)



    financial_products = []



    for bank in FINANCIAL_BANKS:


        items = find_bank_products(

            products,

            bank

        )


        if items:

            financial_products.append(

                max(

                    items,

                    key=lambda x:

                    x["rate"]

                )

            )



    financial_products.sort(

        key=lambda x:

        x["rate"],

        reverse=True

    )



    financial_rank = "-"



    for idx,item in enumerate(

        financial_products,

        start=1

    ):


        if normalize_bank(item["bank"]) == normalize_bank(woori["bank"]):

            financial_rank = idx



    return jsonify({

    "bank":
        woori["bank"],


    "product":
        woori["product"],


    "rate":
        woori["rate"],


    "market_rank":
        rank["rank"],


    "market_total":
        rank["total"],


    "financial_rank":
        financial_rank,


    "average_gap":
        round(
            woori["rate"] - avg,
            2
        ),


    "market_average":
        round(
            avg,
            2
        ),


    "max_gap":
        round(
            woori["rate"] - max(
                x["rate"]
                for x in products
            ),
            2
        ),


    "min_gap":
        round(
            woori["rate"] - min(
                x["rate"]
                for x in products
            ),
            2
        ),


    "highest_rate":
        max(
            x["rate"]
            for x in products
        ),


    "lowest_rate":
        min(
            x["rate"]
            for x in products
        )

})




# -------------------------------
# 시장 TOP10
# -------------------------------

@app.route("/api/rates")

def api_rates():


    products = unique_products(

        build_products(
            "12개월"
        )

    )



    bank_best = get_bank_best_rates(

        products

    )



    bank_best = [

        x

        for x in bank_best

        if x["rate"] > 0

    ]



    bank_best.sort(

        key=lambda x:

        x["rate"],

        reverse=True

    )



    result = []



    for idx,item in enumerate(

        bank_best[:10],

        start=1

    ):


        result.append({

            "rank":

                idx,


            "bank":

                item["bank"],


            "product":

                item["product"],


            "rate":

                item["rate"],


            "change":

                item["change"]

        })



    return jsonify(result)
    # ===================================
# SBRateBot V4 app.py 수정본
# 3/4
# ===================================


# -------------------------------
# 금융지주 저축은행 비교
# -------------------------------

@app.route("/api/financial")

def api_financial():


    products = unique_products(

        build_products(
            "12개월"
        )

    )


    result = []



    for bank in FINANCIAL_BANKS:


        items = find_bank_products(

            products,

            bank

        )


        if items:


            best = max(

                items,

                key=lambda x:

                x["rate"]

            )


            result.append(best)



    result.sort(

        key=lambda x:

        x["rate"],

        reverse=True

    )



    response = []



    for idx,item in enumerate(

        result,

        start=1

    ):


        response.append({

            "rank":

                idx,


            "bank":

                item["bank"],


            "product":

                item["product"],


            "rate":

                item["rate"],


            "change":

                item["change"]

        })



    return jsonify(response)




# -------------------------------
# 전체상품 조회
# -------------------------------

@app.route("/api/products")

def api_products():


    products = []



    period_list = [

        "1개월",

        "3개월",

        "6개월",

        "12개월",

        "24개월",

        "36개월"

    ]



    for period in period_list:


        products.extend(

            build_products(

                period

            )

        )



    products = unique_products(

        products

    )



    products.sort(

        key=lambda x:

        (

            x["period"],

            -x["rate"]

        )

    )



    return jsonify(products)




# -------------------------------
# AI 시장 요약
# -------------------------------

@app.route("/api/ai")

def api_ai():


    try:


        products = load_rates()



        rate_products = []



        for item in products:


            rate = safe_float(

                item.get(

                    "top_12m",

                    0

                )

            )


            if rate and rate > 0:


                data = item.copy()

                data["rate"] = rate


                rate_products.append(data)



        if not rate_products:


            return jsonify({

                "summary":

                    [

                        "금리 데이터가 없습니다."

                    ]

            })



        rate_products.sort(

            key=lambda x:

            x["rate"],

            reverse=True

        )



        total = len(rate_products)



        avg_rate = sum(

            x["rate"]

            for x in rate_products

        ) / total



        highest = rate_products[0]


        lowest = rate_products[-1]



        spread = (

            highest["rate"]

            -

            lowest["rate"]

        )



        summary = []


        summary.append(

            "📊 12개월 정기예금 시장 분석"

        )


        summary.append(

            f"분석상품 : {total}개"

        )


        summary.append(

            f"평균금리 : {avg_rate:.2f}%"

        )


        summary.append(

            f"최고금리 : {highest.get('bank','')} "

            f"{highest['rate']:.2f}%"

        )


        summary.append(

            f"최저금리 : {lowest.get('bank','')} "

            f"{lowest['rate']:.2f}%"

        )


        summary.append(

            f"금리 스프레드 : {spread:.2f}%p"

        )



        if spread >= 0.5:


            summary.append(

                "은행별 금리 경쟁 차이가 큰 시장입니다."

            )


        else:


            summary.append(

                "은행별 금리 차이가 크지 않은 시장입니다."

            )



        if avg_rate >= 3:


            summary.append(

                "평균금리는 3% 이상으로 "

                "금리 경쟁력이 중요한 상황입니다."

            )


        else:


            summary.append(

                "금리 차별화 전략이 중요한 상황입니다."

            )



        # Gemini 시장 분석

        try:


            market_data = json.dumps(

                rate_products[:50],

                ensure_ascii=False

            )


            ai_summary = market_summary(

                market_data

            )


            if ai_summary:


                return jsonify({

                    "summary":

                        ai_summary.split("\n")

                })


        except Exception as e:


            print(

                "Gemini 시장요약 실패:",

                e

            )



        return jsonify({

            "summary":

                summary

        })



    except Exception as e:


        print(

            "AI SUMMARY ERROR:",

            e

        )


        return jsonify({

            "summary":

                [

                    "AI 시장요약 오류"

                ]

        })



# -------------------------------
# AI 검색
# -------------------------------

@app.route(
    "/api/ai/search",
    methods=["POST"]
)

def ai_search():


    try:


        data = request.json or {}



        question = str(

            data.get(

                "question",

                ""

            )

        ).strip()



        if not question:


            return jsonify({

                "answer":

                    "질문을 입력해주세요."

            })



        q = normalize(question)



        products = unique_products(

            build_products(

                "12개월"

            )

        )



        products = [

            x

            for x in products

            if x["rate"] > 0

        ]



        if not products:


            return jsonify({

                "answer":

                    "금리 데이터가 없습니다."

            })



        answer = ""



        # 최저금리

        if any(

            keyword in question

            for keyword in [

                "최저",

                "최저금리",

                "낮은금리",

                "저금리",

                "가장 낮은"

            ]

        ):


            lowest = min(

                products,

                key=lambda x:

                x["rate"]

            )


            answer = (

                "📉 최저금리 상품\n\n"

                f"은행 : {lowest['bank']}\n"

                f"상품 : {lowest['product']}\n"

                f"금리 : {lowest['rate']:.2f}%"

            )


        # 최고금리

        elif any(

            keyword in question

            for keyword in [

                "최고",

                "최고금리",

                "높은금리",

                "가장 높은"

            ]

        ):


            highest = max(

                products,

                key=lambda x:

                x["rate"]

            )


            answer = (

                "📈 최고금리 상품\n\n"

                f"은행 : {highest['bank']}\n"

                f"상품 : {highest['product']}\n"

                f"금리 : {highest['rate']:.2f}%"

            )


        # 은행 경쟁력

        elif any(

            keyword in question

            for keyword in [

                "경쟁력",

                "비교",

                "어때"

            ]

        ):


            target = None



            for bank in FINANCIAL_BANKS + [

                "SBI저축은행",

                "OK저축은행",

                "웰컴저축은행",

                "페퍼저축은행"

            ]:


                if normalize_bank(bank) in normalize_bank(question):

                    target = bank

                    break



            if target:


                items = find_bank_products(

                    products,

                    target

                )


                if items:


                    best = max(

                        items,

                        key=lambda x:

                        x["rate"]

                    )


                    rank = get_market_bank_rank(

                        products,

                        best["bank"]

                    )


                    answer = (

                        f"📌 {best['bank']} 경쟁력 분석\n\n"

                        f"대표상품 : {best['product']}\n"

                        f"금리 : {best['rate']:.2f}%\n"

                        f"시장순위 : {rank['rank']}위 / "

                        f"{rank['total']}개사"

                    )
                    # ===================================
# SBRateBot V4 app.py 수정본
# 4/4
# ===================================


        # -------------------------------
        # 시장 분석
        # -------------------------------

        elif any(

            keyword in question

            for keyword in [

                "시장",

                "동향",

                "전망",

                "상황"

            ]

        ):


            avg = sum(

                x["rate"]

                for x in products

            ) / len(products)



            highest = max(

                products,

                key=lambda x:

                x["rate"]

            )



            lowest = min(

                products,

                key=lambda x:

                x["rate"]

            )



            spread = (

                highest["rate"]

                -

                lowest["rate"]

            )



            answer = (

                "📊 정기예금 시장 분석\n\n"

                f"분석상품 : {len(products)}개\n"

                f"평균금리 : {avg:.2f}%\n"

                f"최고금리 : {highest['bank']} "

                f"{highest['rate']:.2f}%\n"

                f"최저금리 : {lowest['bank']} "

                f"{lowest['rate']:.2f}%\n"

                f"금리 스프레드 : {spread:.2f}%p"

            )



        # -------------------------------
        # 일반 검색
        # -------------------------------

        if not answer:


            result = []



            for item in products:


                bank_match = (

                    q in normalize_bank(

                        item["bank"]

                    )

                )


                product_match = (

                    q in normalize(

                        item["product"]

                    )

                )


                if (

                    bank_match

                    or

                    product_match

                ):


                    result.append(item)



            if result:


                answer = (

                    "📌 검색 결과\n\n"

                )


                for item in result[:10]:


                    answer += (

                        f"은행 : {item['bank']}\n"

                        f"상품 : {item['product']}\n"

                        f"금리 : {item['rate']:.2f}%\n\n"

                    )



        if not answer:


            answer = (

                "검색 결과가 없습니다."

            )



        # -------------------------------
        # Gemini 전문가 의견
        # -------------------------------

        try:


            market_data = json.dumps(

                products[:50],

                ensure_ascii=False

            )



            gemini_result = ask_gemini(

                question,

                market_data

            )



            if (

                gemini_result

                and

                "Gemini 오류"

                not in

                gemini_result

            ):


                answer += (

                    "\n\n"

                    "🤖 AI 전문가 의견\n\n"

                    +

                    gemini_result

                )


        except Exception as e:


            print(

                "Gemini 연결 실패:",

                e

            )



        return jsonify({

            "answer":

                answer

        })



    except Exception as e:


        print(

            "AI SEARCH ERROR:",

            e

        )


        return jsonify({

            "answer":

                "AI 검색 오류가 발생했습니다."

        })




# -------------------------------
# 실행
# -------------------------------

if __name__ == "__main__":


    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )