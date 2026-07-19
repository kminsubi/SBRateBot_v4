# ===================================
# SBRateBot V4 app.py
# 1/4
# ===================================


from flask import Flask, render_template, jsonify, request

from ai.gemini import ask_gemini

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



# 금융지주 계열 저축은행

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



        return []



    except Exception:


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



        return float(value)



    except Exception:


        return None




# -------------------------------
# 문자열 정규화
# 은행명 검색 정확도 개선
# 저축은행 명칭 제거
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

        "-",

        "_"

    ]


    for item in replace_list:


        text = text.replace(

            item,

            ""

        )


    return text.lower()


    # -------------------------------
# AI 검색 Intent 판단 V4.5
# -------------------------------


def detect_intent(question):


    q = normalize(question)



    # -------------------------------
    # 은행 비교 - 높은 금리
    # -------------------------------

    if any(

        x in q

        for x in [

            "보다높",

            "보다좋",

            "이기는",

            "우위",

            "앞서는",

            "경쟁력있는",

            "나은"

        ]

    ):

        return "COMPARE_HIGH"



    # -------------------------------
    # 은행 비교 - 낮은 금리
    # -------------------------------

    if any(

        x in q

        for x in [

            "보다낮",

            "낮은곳",

            "밀리는",

            "뒤처지는",

            "열위"

        ]

    ):

        return "COMPARE_LOW"



    # -------------------------------
    # 경쟁력 분석
    # -------------------------------

    if any(

        x in q

        for x in [

            "경쟁력",

            "경쟁",

            "비교",

            "어때",

            "괜찮",

            "평가",

            "위치"

        ]

    ):

        return "COMPETITIVENESS"



    # -------------------------------
    # 시장 현황
    # -------------------------------

    if any(

        x in q

        for x in [

            "시장현황",

            "시장상황",

            "현재위치",

            "시장위치",

            "순위"

        ]

    ):

        return "MARKET_STATUS"



    # -------------------------------
    # 최고 금리
    # -------------------------------

    if any(

        x in q

        for x in [

            "최고금리",

            "가장높",

            "높은금리",

            "1위금리"

        ]

    ):

        return "TOP_RATE"



    # -------------------------------
    # 최저 금리
    # -------------------------------

    if any(

        x in q

        for x in [

            "최저금리",

            "가장낮",

            "낮은금리"

        ]

    ):

        return "LOW_RATE"



    return "UNKNOWN"


# -------------------------------
# 저축은행명 별칭 매핑
# -------------------------------

BANK_ALIAS = {

    # 우리금융저축은행
    "우리금융저축은행": "우리금융저축은행",
    "우리금융": "우리금융저축은행",
    "우리저축": "우리금융저축은행",
    "우리저축은행": "우리금융저축은행",
    "우리": "우리금융저축은행",


    # 신한저축은행
    "신한저축은행": "신한저축은행",
    "신한저축": "신한저축은행",
    "신한": "신한저축은행",


    # 하나저축은행
    "하나저축은행": "하나저축은행",
    "하나저축": "하나저축은행",
    "하나": "하나저축은행",


    # KB저축은행
    "KB저축은행": "KB저축은행",
    "KB저축": "KB저축은행",
    "kb": "KB저축은행",
    "국민": "KB저축은행",


    # SBI저축은행
    "SBI저축은행": "SBI저축은행",
    "SBI저축": "SBI저축은행",
    "SBI": "SBI저축은행",
    "sbi": "SBI저축은행",


    # OK저축은행
    "OK저축은행": "OK저축은행",
    "OK저축": "OK저축은행",
    "OK": "OK저축은행",
    "ok": "OK저축은행",


    # 페퍼저축은행
    "페퍼저축은행": "페퍼저축은행",
    "페퍼저축": "페퍼저축은행",
    "페퍼": "페퍼저축은행",


    # 웰컴저축은행
    "웰컴저축은행": "웰컴저축은행",
    "웰컴": "웰컴저축은행",


    # 모아저축은행
    "모아저축은행": "모아저축은행",
    "모아": "모아저축은행",


    # 한국투자저축은행
    "한국투자저축은행": "한국투자저축은행",
    "한국투자": "한국투자저축은행",


    # 대원저축은행
    "대원저축은행": "대원저축은행",
    "대원": "대원저축은행"

}



def resolve_bank_name(question):


    print(

        "resolve 입력:",

        question

    )


    q = normalize(question)


    print(

        "normalize 결과:",

        q

    )


        # -------------------------------
    # 기존 별칭 우선 검색
    # -------------------------------

    for keyword, bank_name in sorted(

        BANK_ALIAS.items(),

        key=lambda x: len(x[0]),

        reverse=True

    ):


        if normalize(keyword) in q:


            print(

                "별칭 매칭:",

                keyword,

                "->",

                bank_name

            )


            return bank_name.replace(

                "저축은행",

                ""

            )



    # -------------------------------
    # 전체 저축은행 자동 검색
    # -------------------------------

    try:


        products = build_products()


        print(

            "AI 검색 질문:",

            question

        )


        print(

            "정규화 질문:",

            q

        )


        print(

            "은행 샘플:",

            [

                x.get("bank")

                for x in products[:10]

            ]

        )



        banks = sorted(

            set(

                x.get("bank")

                for x in products

                if x.get("bank")

            ),

            key=len,

            reverse=True

        )



        for bank in banks:


            bank_normal = normalize(bank)



            if bank_normal in q:


                return bank



            if (

                bank_normal + "저축은행"

            ) in q:


                return bank



    except Exception as e:


        print(

            "은행 자동검색 오류:",

            e

        )



    return None


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

    or

    item.get(

        "change"

    )

    or

    item.get(

        "change_rate"

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
# 상품 중복 제거
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




# -------------------------------
# 은행별 최고 금리
# -------------------------------


def get_bank_best_rates(products):

    bank_map = {}

    for item in products:

        bank = item["bank"]

        if not bank:
            continue


        if (
            bank not in bank_map
            or
            item["rate"] > bank_map[bank]["rate"]
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
# 은행 시장 현황 분석
# -------------------------------

def analyze_bank_status(
    products,
    bank_name
):


    bank_products = find_bank_products(

        products,

        bank_name

    )


    if not bank_products:

        return None



    bank_products = [

        x

        for x in bank_products

        if x["rate"] > 0

    ]



    if not bank_products:

        return None



    bank_products.sort(

        key=lambda x:

            x["rate"],

        reverse=True

    )



    best = bank_products[0]



    market_rates = [

        x["rate"]

        for x in products

        if x["rate"] > 0

    ]



    avg_rate = sum(

        market_rates

    ) / len(market_rates)



    rank = get_market_bank_rank(

        products,

        bank_name

    )



    # -------------------------------
    # 경쟁사 분석
    # -------------------------------

    higher = [

        x

        for x in products

        if (

            x["rate"]

            >

            best["rate"]

        )

        and

        normalize(x["bank"])

        !=

        normalize(bank_name)

    ]



    lower = [

        x

        for x in products

        if (

            x["rate"]

            <

            best["rate"]

        )

        and

        normalize(x["bank"])

        !=

        normalize(bank_name)

    ]



    higher.sort(

        key=lambda x:

            x["rate"],

        reverse=True

    )



    lower.sort(

        key=lambda x:

            x["rate"],

        reverse=True

    )



    market_position = round(

        (

            rank["rank"]

            /

            rank["total"]

        )

        *

        100,

        1

    )



        # -------------------------------
    # 상위 경쟁사 분석 V4.5
    # -------------------------------

    bank_best_rates = {}


    for item in products:


        bank = item.get(

            "bank"

        )


        rate = item.get(

            "rate",

            0

        )


        if not bank:

            continue


        if rate <= 0:

            continue



        if (

            bank not in bank_best_rates

            or rate >

            bank_best_rates[bank]

        ):


            bank_best_rates[bank] = rate



    top10_rates = sorted(

        bank_best_rates.values(),

        reverse=True

    )[:10]



    if top10_rates:


        top10_avg = round(

            sum(top10_rates)

            /

            len(top10_rates),

            2

        )


    else:


        top10_avg = 0



    top10_gap = round(

        best["rate"]

        -

        top10_avg,

        2

    )



    if rank["rank"] <= 10:


        position_text = "상위권"


    elif rank["rank"] <= 40:


        position_text = "중위권"


    else:


        position_text = "하위권"



    return {


        "bank":

            bank_name,


        "product":

            best.get(

                "product",

                "-"

            ),


        "rate":

            best["rate"],


        "rank":

            rank["rank"],


        "total":

            rank["total"],


        "avg_gap":

            round(

                best["rate"]

                -

                avg_rate,

                2

            ),


        "market_position":

            market_position,


        "position_text":

            position_text,


        "top10_avg":

            top10_avg,


        "top10_gap":

            top10_gap,


        "higher":

            higher,


        "lower":

            lower

    }



# -------------------------------
# 금리 증감 표시
# 대시보드 공통 규칙
# 상승 : 파란색 + 표시
# 하락 : 빨간색 ▲ 표시
# -------------------------------

def format_change(change):

    if change > 0:

        return (

            f'<span class="rate-change increase">'

            f'+{change:.2f}%p'

            f'</span>'

        )


    elif change < 0:

        return (

            f'<span class="rate-change decrease">'

            f'▲{abs(change):.2f}%p'

            f'</span>'

        )


    else:

        return "0.00%p"





def get_top_products(products, count=5):

    return sort_rate_products(
        products,
        True
    )[:count]



def get_bottom_products(products, count=5):

    return sort_rate_products(
        products,
        False
    )[:count]



def filter_over_rate(products, rate):

    return [
        x
        for x in products
        if x["rate"] >= rate
    ]



def filter_under_rate(products, rate):

    return [
        x
        for x in products
        if x["rate"] <= rate
    ]



def search_product_keyword(products, keyword):

    keyword = normalize(keyword)

    result = []

    for item in products:

        if (
            keyword in normalize(item["bank"])
            or
            keyword in normalize(item["product"])
        ):

            result.append(item)


    return result



def compare_two_banks(products, bank1, bank2):

    bank1_items = find_bank_products(
        products,
        bank1
    )

    bank2_items = find_bank_products(
        products,
        bank2
    )


    if not bank1_items or not bank2_items:

        return None


    bank1_best = max(
        bank1_items,
        key=lambda x:x["rate"]
    )


    bank2_best = max(
        bank2_items,
        key=lambda x:x["rate"]
    )


    return {

        "bank1": bank1_best,

        "bank2": bank2_best,

        "difference":
            round(
                bank1_best["rate"]
                -
                bank2_best["rate"],
                2
            )

    }



# -------------------------------
# 질문 내 은행명 찾기 V4.3
# -------------------------------

def find_target_bank(question):


    q = normalize(
        question
    )


    bank_alias = {


        "우리금융저축은행":
            "우리금융저축은행",

        "우리금융":
            "우리금융저축은행",


        "우리저축":
            "우리금융저축은행",



        "신한저축은행":
            "신한저축은행",

        "신한":
            "신한저축은행",



        "하나저축은행":
            "하나저축은행",

        "하나":
            "하나저축은행",



        "KB저축은행":
            "KB저축은행",

        "KB":
            "KB저축은행",

        "kb":
            "KB저축은행",



        "SBI저축은행":
            "SBI저축은행",

        "SBI":
            "SBI저축은행",

        "sbi":
            "SBI저축은행",



        "OK저축은행":
            "OK저축은행",

        "OK":
            "OK저축은행",

        "ok":
            "OK저축은행",



        "웰컴저축은행":
            "웰컴저축은행",

        "웰컴":
            "웰컴저축은행",



        "페퍼저축은행":
            "페퍼저축은행",

        "페퍼":
            "페퍼저축은행",



        "모아저축은행":
            "모아저축은행",

        "모아":
            "모아저축은행",



        "한국투자저축은행":
            "한국투자저축은행",

        "한국투자":
            "한국투자저축은행",



        "대원저축은행":
            "대원저축은행",

        "대원":
            "대원저축은행"

    }



    # 긴 이름 먼저 검사

    for key in sorted(
        bank_alias.keys(),
        key=len,
        reverse=True
    ):


        if normalize(key) in q:

            return bank_alias[key]



    return None

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

            "product_count":0,

            "max_rate":"0.00%",

            "average_rate":"0.00%",

            "min_rate":"0.00%"

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

    


    if not products:


        return jsonify({


            "bank":

                "우리금융저축은행"


        })



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



    # -------------------------------
    # 시장 순위
    # -------------------------------


    rank = get_market_bank_rank(

        products,

        woori["bank"]

    )



    # -------------------------------
    # 시장 평균 / 최고 / 최저
    # -------------------------------


    avg_rate = sum(

        x["rate"]

        for x in products

    ) / len(products)



    highest_rate = max(

        x["rate"]

        for x in products

    )



    lowest_rate = min(

        x["rate"]

        for x in products

    )



    # -------------------------------
    # 금융지주 순위
    # -------------------------------


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


        if normalize(item["bank"]) == normalize(woori["bank"]):


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



        # 평균금리 대비

        "average_gap":

            round(

                woori["rate"] - avg_rate,

                2

            ),



        # 최고금리 대비

        "highest_gap":

            round(

                woori["rate"] - highest_rate,

                2

            ),



        # 최저금리 대비

        "lowest_gap":

            round(

                woori["rate"] - lowest_rate,

                2

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


            # -------------------------------
            # 금리 증감 표시
            # 상승 : 파란색
            # 하락 : 빨간색
            # -------------------------------

            "change":
                item["change"],


            "change_html":

                (
                    '<span class="rate-change increase">'
                    f'+{item["change"]:.2f}%p'
                    '</span>'

                    if item["change"] > 0

                    else

                    (
                        '<span class="rate-change decrease">'
                        f'▲{abs(item["change"]):.2f}%p'
                        '</span>'
                    )

                    if item["change"] < 0

                    else

                    '<span class="rate-change">'
                    '0.00%p'
                    '</span>'
                )

        })



    return jsonify(response)




# -------------------------------
# 전체상품 조회
# -------------------------------


@app.route("/api/products")

def api_products():


    products = []



    for period in PERIOD_MAP:


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

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            products = json.load(f)



        if isinstance(products, dict):

            products = products.get(
                "REC",
                []
            )



        if not products:

            return jsonify({

                "summary":[

                    "시장 데이터를 불러올 수 없습니다."

                ]

            })



        rate_products = []



        for item in products:


            try:


                rate = float(

                    str(

                        item.get("top_12m")

                        or item.get("rate")

                        or 0

                    )
                    .replace(
                        ",",
                        ""
                    )

                )


                if rate > 0:

                    item["rate"] = rate

                    rate_products.append(item)



            except:

                continue




        if not rate_products:


            return jsonify({

                "summary":[

                    "금리 데이터가 없습니다."

                ]

            })




        rate_products.sort(

            key=lambda x:x["rate"],

            reverse=True

        )




        total = len(rate_products)



        avg_rate = sum(

            x["rate"]

            for x in rate_products

        ) / total




        highest = rate_products[0]

        lowest = rate_products[-1]

        highest_gap = (

            highest["rate"]

            -

            avg_rate

        )


        lowest_gap = (

            lowest["rate"]

            -

            avg_rate

        )


        if highest_gap >= 0:

            highest_gap_text = (

                f"+{highest_gap:.2f}%p"

            )

        else:

            highest_gap_text = (

                f"▲{abs(highest_gap):.2f}%p"

            )


        if lowest_gap < 0:

            lowest_gap_text = (

                f"▲{abs(lowest_gap):.2f}%p"

            )

        else:

            lowest_gap_text = (

                f"+{lowest_gap:.2f}%p"

            )



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

            f"최고금리 : "

            f"{highest.get('bank','')} "

            f"{highest['rate']:.2f}%"

        )



        summary.append(

            f"최저금리 : "

            f"{lowest.get('bank','')} "

            f"{lowest['rate']:.2f}%"

        )



        summary.append(

            f"금리 스프레드 : {spread:.2f}%p"

        )




        if spread >= 0.5:


            summary.append(

                "은행별 금리 경쟁 차이가 큰 시장으로 "

                "최고금리 상품 중심의 경쟁이 진행되고 있습니다."

            )


        else:


            summary.append(

                "은행별 금리 차이가 크지 않은 "

                "안정적인 금리 경쟁 시장입니다."

            )




        if avg_rate >= 3:


            summary.append(

                "평균금리는 3% 이상으로 "

                "예금 유치를 위한 금리 경쟁력이 중요한 상황입니다."

            )


        else:


            summary.append(

                "평균금리는 낮은 수준으로 "

                "고객 선택 시 금리 차별화가 중요합니다."

            )




        return jsonify({

            "summary":summary

        })




    except Exception as e:


        print(

            "AI 시장 분석 오류:",

            e

        )


        return jsonify({

            "summary":[

                "AI 시장 분석 오류가 발생했습니다."

            ]

        })


# -------------------------------
# AI 검색 V4.1
# Python Intent + Gemini 분리
# -------------------------------


@app.route(
    "/api/ai/search",
    methods=["POST"]
)
def ai_search():

    try:

        data = request.json


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



        q = normalize(

            question

        )



        # -------------------------------
        # AI Intent 판단 V4.5
        # -------------------------------

        intent = detect_intent(

            question

        )


        print(

            "AI INTENT:",

            intent

        )

        # -------------------------------
        # 은행명 자동 인식
        # -------------------------------

        target_bank = resolve_bank_name(question)


        print(
            "TARGET BANK:",
            target_bank
        )

        # -------------------------------
        # 검색 기간 선택
        # 기본 12개월
        # -------------------------------

        search_period = "12개월"


        if "1개월" in question:

            search_period = "1개월"

        elif "3개월" in question:

            search_period = "3개월"

        elif "6개월" in question:

            search_period = "6개월"

        elif "24개월" in question:

            search_period = "24개월"

        elif "36개월" in question:

            search_period = "36개월"



        products = unique_products(

            build_products(

                search_period

            )

        )



        products = [

            x

            for x in products

            if x["rate"] > 0

        ]

        # -------------------------------
        # 은행 시장 분석
        # -------------------------------

        bank_analysis = None


        if target_bank:

            bank_analysis = analyze_bank_status(

                products,

                target_bank

            )



        answer = ""

                # -------------------------------
        # 우리금융 경쟁력 우선 처리 V4.5
        # -------------------------------

        if (

            intent == "COMPETITIVENESS"

            and

            (

                "우리금융"

                in question

                or

                "우리금융저축은행"

                in question

            )

        ):


            if bank_analysis:


                gap = bank_analysis["avg_gap"]



                if gap > 0:

                    gap_text = (

                        f'<span class="rate-change increase">'

                        f'+{gap:.2f}%p'

                        f'</span>'

                    )


                    evaluation = (

                        "시장 평균 대비 높은 금리로 "

                        "금리 경쟁력이 양호합니다."

                    )


                elif gap < 0:

                    gap_text = (

                        f'<span class="rate-change decrease">'

                        f'▲{abs(gap):.2f}%p'

                        f'</span>'

                    )


                    evaluation = (

                        "시장 평균 대비 낮은 금리로 "

                        "금리 경쟁력 개선이 필요합니다."

                    )


                else:

                    gap_text = "0.00%p"


                    evaluation = (

                        "시장 평균 수준의 금리입니다."

                    )



                answer = (

                    "🏦 우리금융저축은행 경쟁력 분석\n\n"

                    f"기준기간 : {search_period}\n\n"

                    f"현재금리 : {bank_analysis['rate']:.2f}%\n\n"

                    f"시장순위 : "

                    f"{bank_analysis['rank']}위 / "

                    f"{bank_analysis['total']}개사\n\n"

                    f"평균금리 대비 : "

                    f"{gap_text}\n\n"

                    f"평가 : {evaluation}"

                )

        

        # -------------------------------
        # 전체 시장현황 검색
        # -------------------------------

        if (

            not bank_analysis

            and

            any(

                x in question

                for x in [

                    "시장현황",

                    "시장 현황",

                    "시장상황",

                    "금리 상황",

                    "금리현황",

                    "금리 현황"

                ]

            )

        ):


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


            avg_rate = sum(

                x["rate"]

                for x in products

            ) / len(products)



            spread = (

                highest["rate"]

                -

                lowest["rate"]

            )


            highest_gap = (

                highest["rate"]

                -

                avg_rate

            )


            lowest_gap = (

                lowest["rate"]

                -

                avg_rate

            )



            if highest_gap >= 0:

                highest_gap_text = (

                    f'<span class="rate-change increase">'

                    f'+{highest_gap:.2f}%p'

                    f'</span>'

                )

            else:

                highest_gap_text = (

                    f'<span class="rate-change decrease">'

                    f'▲{abs(highest_gap):.2f}%p'

                    f'</span>'

                )



            if lowest_gap < 0:

                lowest_gap_text = (

                    f'<span class="rate-change decrease">'

                    f'▲{abs(lowest_gap):.2f}%p'

                    f'</span>'

                )

            else:

                lowest_gap_text = (

                    f'<span class="rate-change increase">'

                    f'+{lowest_gap:.2f}%p'

                    f'</span>'

                )



            answer = (

                f"■ 정기예금 시장현황\n\n"

                f"기준기간 : {search_period}\n\n"

                f"상품 수 : {len(products)}개\n\n"

                f"최고금리 : {highest['rate']:.2f}%\n"

                f"최고상품 : {highest['bank']} / {highest['product']}\n\n"

                f"평균금리 : {avg_rate:.2f}%\n\n"

                f"최저금리 : {lowest['rate']:.2f}%\n"

                f"최저상품 : {lowest['bank']} / {lowest['product']}\n\n"

                f"최고금리-평균금리 : {highest_gap_text}<br>"

                f"최저금리-평균금리 : {lowest_gap_text}"

            )



        # -------------------------------
        # 은행 시장현황 검색
        # -------------------------------

        if (

            bank_analysis

            and

            any(

                x in question

                for x in [

                    "시장현황",

                    "현황",

                    "상황",

                    "시장",

                    "순위",

                ]

            )

        ):


            gap = bank_analysis["avg_gap"]



            if gap > 0:

                gap_text = (

                    f'<span class="rate-change increase">'

                    f'+{gap:.2f}%p'

                    f'</span>'

                )


            elif gap < 0:

                gap_text = (

                    f'<span class="rate-change decrease">'

                    f'▲{abs(gap):.2f}%p'

                    f'</span>'

                )


            else:

                gap_text = "0.00%p"



            answer = (

                f"■ {bank_analysis['bank']} 시장현황\n\n"

                f"기준기간 : {search_period}\n\n"

                f"대표상품 : {bank_analysis['product']}\n"

                f"현재금리 : {bank_analysis['rate']:.2f}%\n\n"

                f"시장순위 : {bank_analysis['rank']}위 / {bank_analysis['total']}개\n"

                f"평균금리 대비 : {gap_text}"

            )



        # -------------------------------
        # 은행 경쟁력 분석
        # -------------------------------

        elif (

            bank_analysis

            and

            any(

                x in question

                for x in [

                    "경쟁력",

                    "경쟁",

                    "비교",

                    "어때",

                    "괜찮",

                    "괜찮아",

                    "평가",

                    "위치"

                ]

            )

        ):


            gap = bank_analysis["avg_gap"]



            if gap > 0:

                gap_text = (

                    f'<span class="rate-change increase">'

                    f'+{gap:.2f}%p'

                    f'</span>'

                )


                evaluation = (

                    "시장 평균 대비 높은 금리로 "

                    "금리 경쟁력이 양호합니다."

                )


            elif gap < 0:

                gap_text = (

                    f'<span class="rate-change decrease">'

                    f'▲{abs(gap):.2f}%p'

                    f'</span>'

                )


                evaluation = (

                    "시장 평균 대비 낮은 금리로 "

                    "금리 경쟁력 개선이 필요합니다."

                )


            else:

                gap_text = "0.00%p"


                evaluation = (

                    "시장 평균 수준입니다."

                )



                answer = (

                    f"■ {bank_analysis['bank']} 경쟁력 분석\n\n"

                    f"기준기간 : {search_period}\n\n"

                    f"현재금리 : {bank_analysis['rate']:.2f}%\n\n"

                    f"시장순위 : "

                    f"{bank_analysis['rank']}위 / "

                    f"{bank_analysis['total']}개사\n\n"

                    f"시장 위치 : "

                    f"{bank_analysis['position_text']}\n\n"

                    f"평균금리 대비 : "

                    f"{gap_text}\n\n"

                    f"TOP10 평균금리 : "

                    f"{bank_analysis['top10_avg']:.2f}%\n\n"

                    f"TOP10 대비 : "

                    f"{format_change(bank_analysis['top10_gap'])}\n\n"

                    f"평가 : "

                    f"{evaluation}"

                )



                # -------------------------------
                # 경쟁사 비교 TOP5 추가
                # -------------------------------

                if bank_analysis.get("higher"):


                    answer += (

                        "\n\n📈 "

                        f"{bank_analysis['bank']}보다 높은 금리 TOP5\n\n"

                    )


                    for item in bank_analysis["higher"][:5]:


                        diff = round(

                            item["rate"]

                            -

                            bank_analysis["rate"],

                            2

                        )


                        answer += (

                            f"{item['bank']} "

                            f"{item['rate']:.2f}% "

                            f"(+{diff:.2f}%p)\n"

                        )



                if bank_analysis.get("lower"):


                    answer += (

                        "\n\n📉 "

                        f"{bank_analysis['bank']}보다 낮은 금리 TOP5\n\n"

                    )


                    for item in bank_analysis["lower"][:5]:


                        diff = round(

                            bank_analysis["rate"]

                            -

                            item["rate"],

                            2

                        )


                        answer += (

                            f"{item['bank']} "

                            f"{item['rate']:.2f}% "

                            f"(▲{diff:.2f}%p)\n"

                        )



        # -------------------------------
        # 최고 금리
        # -------------------------------


        elif any(

            x in question

            for x in [

                "최고금리",

                "최고 금리",

                "가장 높은",

                "높은 금리"

            ]

        ):


            item = max(

                products,

                key=lambda x:

                    x["rate"]

            )


            rank = get_market_bank_rank(

                products,

                item["bank"]

            )


            answer = (

                f"📈 {search_period} 최고금리\n\n"

                f"은행 : {item['bank']}\n"

                f"상품 : {item['product']}\n"

                f"최고금리 : {item['rate']:.2f}%\n"

                f"시장순위 : {rank['rank']}위 / {rank['total']}개사"

            )



        
        # -------------------------------
        # 최저 금리
        # -------------------------------


        elif any(

            x in question

            for x in [

                "최저금리",

                "최저 금리",

                "가장 낮은",

                "낮은 금리"

            ]

        ):


            item = min(

                products,

                key=lambda x:

                    x["rate"]

            )


            rank = get_market_bank_rank(

                products,

                item["bank"]

            )


            answer = (

                f"📉 {search_period} 최저금리\n\n"

                f"은행 : {item['bank']}\n"

                f"상품 : {item['product']}\n"

                f"최저금리 : {item['rate']:.2f}%\n"

                f"시장순위 : {rank['rank']}위 / {rank['total']}개사"

            )



        # -------------------------------
        # TOP 검색
        # 예) 3개월 TOP5
        # -------------------------------


        elif (

            "TOP"

            in question.upper()

            or

            "상위"

            in question

        ):


            count = extract_number(

                question

            )


            if not count:

                count = 5



            items = get_top_products(

                products,

                int(count)

            )



            answer = (

                f"🏆 {search_period} 금리 TOP {int(count)}\n\n"

            )


            for idx,item in enumerate(

                items,

                start=1

            ):


                answer += (

                    f"{idx}. "

                    f"{item['bank']} "

                    f"{item['product']} "

                    f"{item['rate']:.2f}%\n"

                )



        # -------------------------------
        # 하위 검색
        # -------------------------------


        elif (

            "하위"

            in question

            or

            "낮은순"

            in question

        ):


            count = extract_number(

                question

            )


            if not count:

                count = 5



            items = get_bottom_products(

                products,

                int(count)

            )



            answer = (

                f"📉 {search_period} 낮은 금리 TOP {int(count)}\n\n"

            )


            for idx,item in enumerate(

                items,

                start=1

            ):


                answer += (

                    f"{idx}. "

                    f"{item['bank']} "

                    f"{item['product']} "

                    f"{item['rate']:.2f}%\n"

                )
                        # -------------------------------
        # 금리 이상 검색
        # 예) 3% 이상
        # -------------------------------

        elif (

            "이상"

            in question

            and extract_number(question)

        ):


            rate = extract_number(

                question

            )


            items = filter_over_rate(

                products,

                rate

            )


            answer = (

                f"📌 {search_period} {rate}% 이상 상품\n\n"

            )


            for item in items[:10]:


                answer += (

                    f"{item['bank']} "

                    f"{item['product']} "

                    f"{item['rate']:.2f}%\n"

                )



        # -------------------------------
        # 금리 이하 검색
        # 예) 3% 이하
        # -------------------------------

        elif (

            "이하"

            in question

            and extract_number(question)

        ):


            rate = extract_number(

                question

            )


            items = filter_under_rate(

                products,

                rate

            )


            answer = (

                f"📌 {search_period} {rate}% 이하 상품\n\n"

            )


            for item in items[:10]:


                answer += (

                    f"{item['bank']} "

                    f"{item['product']} "

                    f"{item['rate']:.2f}%\n"

                )



        # -------------------------------
        # 은행 비교
        # 예) KB vs 신한
        # -------------------------------

        elif (

            "vs"

            in q

            or

            "비교"

            in question

        ):


            banks = []


            for bank in FINANCIAL_BANKS + [

                "KB저축은행",

                "신한저축은행",

                "SBI저축은행",

                "OK저축은행"

            ]:


                if normalize(bank) in q:

                    banks.append(bank)



            if len(banks) >= 2:


                result = compare_two_banks(

                    products,

                    banks[0],

                    banks[1]

                )


                if result:


                    answer = (

                        "⚖️ 은행 비교\n\n"

                        f"{banks[0]}\n"

                        f"금리 : {result['bank1']['rate']:.2f}%\n\n"

                        f"{banks[1]}\n"

                        f"금리 : {result['bank2']['rate']:.2f}%\n\n"

                        f"차이 : "

                        f"{result['difference']:.2f}%p"

                    )



                # -------------------------------
        # 우리금융 자연어 경쟁력 분석
        # 예)
        # 우리금융 경쟁력 어때
        # 우리금융저축은행 경쟁력
        # 우리금융보다 높은 곳
        # 우리금융보다 낮은 곳
        # -------------------------------

        elif (

            (
                "우리금융"
                in question

                or

                "우리금융저축은행"
                in question
            )

            and any(

                x in question

                for x in [

                    "경쟁력",
                    "어때",
                    "위치",
                    "비교",
                    "보다",
                    "높은",
                    "낮은",
                    "상위",
                    "하위"

                ]

            )

        ):


            woori_items = find_bank_products(

                products,

                "우리금융저축은행"

            )


            if woori_items:


                woori_best = max(

                    woori_items,

                    key=lambda x:

                        x["rate"]

                )


                rank = get_market_bank_rank(

                    products,

                    woori_best["bank"]

                )


                avg_rate = sum(

                    x["rate"]

                    for x in products

                ) / len(products)



                bank_best_rates = get_bank_best_rates(
                    products
                )


                higher = [

                    x

                    for x in bank_best_rates

                    if (

                        x["rate"]

                        >

                        woori_best["rate"]

                    )

                    and

                    normalize(x["bank"])

                    !=

                    normalize(woori_best["bank"])

                ]



                lower = [

                    x

                    for x in bank_best_rates

                    if (

                        x["rate"]

                        <

                        woori_best["rate"]

                    )

                    and

                    normalize(x["bank"])

                    !=

                    normalize(woori_best["bank"])

                ]



                higher.sort(

                    key=lambda x:

                        x["rate"],

                    reverse=True

                )


                lower.sort(

                    key=lambda x:

                        x["rate"],


                )



                gap = round(

                    woori_best["rate"]

                    -

                    avg_rate,

                    2

                )



                if gap > 0:

                    gap_text = (

                        f'<span class="rate-change increase">'

                        f'+{gap:.2f}%p'

                        f'</span>'

                    )


                    evaluation = (

                        "시장 평균 대비 높은 금리로 "

                        "금리 경쟁력이 양호합니다."

                    )


                elif gap < 0:

                    gap_text = (

                        f'<span class="rate-change decrease">'

                        f'▲{abs(gap):.2f}%p'

                        f'</span>'

                    )


                    evaluation = (

                        "시장 평균 대비 낮은 금리로 "

                        "금리 경쟁력 개선이 필요합니다."

                    )


                else:

                    gap_text = "0.00%p"


                    evaluation = (

                        "시장 평균 수준의 금리입니다."

                    )



                market_position = round(

                    (

                        (

                            rank["total"]

                            -

                            rank["rank"]

                            +

                            1

                        )

                        /

                        rank["total"]

                    )

                    *

                    100,

                    1

                )



                answer = (

                    "🏦 우리금융저축은행 경쟁력 분석\n\n"

                    f"기준기간 : {search_period}\n\n"

                    f"현재금리 : {woori_best['rate']:.2f}%\n\n"

                    f"시장순위 : {rank['rank']}위 / "

                    f"{rank['total']}개사\n"

                    f"시장 위치 : 상위 "

                    f"{market_position:.1f}% 수준\n\n"

                    f"평균금리 대비 : {gap_text}\n\n"

                    f"평가 : {evaluation}\n\n"

                    f"📈 우리보다 높은 금리 : "

                    f"{len(higher)}개사\n"

                    f"📉 우리보다 낮은 금리 : "

                    f"{len(lower)}개사\n"

                )



                if higher:


                    answer += (

                        "\n📈 우리보다 높은 경쟁사 TOP5\n\n"

                    )


                    for item in higher[:5]:


                        diff = round(

                            item["rate"]

                            -

                            woori_best["rate"],

                            2

                        )


                        diff_text = (

                            f'<span class="rate-change increase">'

                            f'+{diff:.2f}%p'

                            f'</span>'

                        )


                        answer += (

                            f"{item['bank']} "

                            f"{item['rate']:.2f}% "

                            f"{diff_text}\n"

                        )



                if lower:


                    answer += (

                        "\n📉 우리보다 낮은 경쟁사 TOP5\n\n"

                    )


                    for item in lower[:5]:


                        diff = round(

                            woori_best["rate"]

                            -

                            item["rate"],

                            2

                        )


                        diff_text = (

                            f'<span class="rate-change decrease">'

                            f'▲{diff:.2f}%p'

                            f'</span>'

                        )


                        answer += (

                            f"{item['bank']} "

                            f"{item['rate']:.2f}% "

                            f"{diff_text}\n"

                        )

                # -------------------------------
        # 특정 은행 대비 금리 비교 검색 V4.5
        #
        # Intent 기반 비교 처리
        #
        # COMPARE_HIGH
        # - 대원보다 높은 곳
        # - 페퍼 이기는 곳
        #
        # COMPARE_LOW
        # - 모아보다 낮은 곳
        #
        # 기준:
        # - 은행별 최고금리 기준 비교
        # - 전체 저축은행 대상
        # -------------------------------


        elif (

            intent in [

                "COMPARE_HIGH",

                "COMPARE_LOW"

            ]

        ):


            # -------------------------------
            # 비교 대상 은행 찾기
            # -------------------------------

            target_bank = find_target_bank(

                question

            )


            if target_bank:


                # -------------------------------
                # 대상 은행 최고금리
                # -------------------------------

                target_items = find_bank_products(

                    products,

                    target_bank

                )


                if target_items:


                    target_rate = max(

                        x["rate"]

                        for x in target_items

                    )


                    rank = get_market_bank_rank(

                        products,

                        target_bank

                    )


                    # -------------------------------
                    # 시장 평균금리 계산
                    #
                    # 기준:
                    # - 12개월 기준
                    # - 0% 제외
                    # -------------------------------

                    valid_rates = []


                    for item in products:


                        rate = float(

                            item.get(

                                "top_12m"

                            )

                            or item.get(

                                "rate"

                            )

                            or 0

                        )


                        if rate > 0:

                            valid_rates.append(

                                rate

                            )



                    if valid_rates:


                        market_average = (

                            sum(valid_rates)

                            /

                            len(valid_rates)

                        )


                    else:


                        market_average = 0



                    # -------------------------------
                    # 은행별 최고금리 생성
                    # -------------------------------

                    bank_best_rates = {}


                    for item in products:


                        bank = item.get(

                            "bank"

                        )


                        rate = float(

                            item.get(

                                "top_12m"

                            )

                            or item.get(

                                "rate"

                            )

                            or 0

                        )


                        if not bank:

                            continue


                        if rate <= 0:

                            continue



                        if (

                            bank not in bank_best_rates

                            or rate >

                            bank_best_rates[bank]

                        ):


                            bank_best_rates[bank] = rate



                    gap = round(

                        target_rate

                        -

                        market_average,

                        2

                    )



                    if gap > 0:


                        gap_text = (

                            f'<span class="rate-change increase">'

                            f'+{gap:.2f}%p'

                            f'</span>'

                        )


                    elif gap < 0:


                        gap_text = (

                            f'<span class="rate-change decrease">'

                            f'▲{abs(gap):.2f}%p'

                            f'</span>'

                        )


                    else:


                        gap_text = "0.00%p"

                        id="part2"
                    # -------------------------------
                    # 비교 대상 제외 후 은행 리스트 생성
                    # -------------------------------

                    bank_products = []


                    for bank, rate in bank_best_rates.items():


                        if normalize(bank) == normalize(target_bank):

                            continue



                        bank_products.append({

                            "bank": bank,

                            "rate": rate

                        })



                    # -------------------------------
                    # 우위 / 열위 판단
                    # -------------------------------

                    higher_words = [

                        "높은",

                        "좋은",

                        "우위",

                        "앞서는",

                        "경쟁력",

                        "나은",

                        "이기는",

                        "우세",

                        "우세한",

                        "상위",

                        "앞선",

                        "더 높은"

                    ]



                    is_higher = any(

                        x in question

                        for x in higher_words

                    )



                    if is_higher:


                        result = [

                            x

                            for x in bank_products

                            if x["rate"] > target_rate

                        ]


                        result.sort(

                            key=lambda x:x["rate"],

                            reverse=True

                        )


                        title = (

                            f"📈 {target_bank} 대비 우위 은행"

                        )


                    else:


                        result = [

                            x

                            for x in bank_products

                            if x["rate"] < target_rate

                        ]


                        result.sort(

                            key=lambda x:x["rate"],

                            reverse=True

                        )


                        title = (

                            f"📉 {target_bank} 대비 열위 은행"

                        )



                    answer = (

                        f"{title}\n\n"

                        f"{target_bank} 최고금리 : "

                        f"{target_rate:.2f}%\n\n"

                        f"시장순위 : "

                        f"{rank['rank']}위 / "

                        f"{rank['total']}개사\n\n"

                        f"저축은행 최고금리 평균 대비 : "

                        f"{gap_text}\n\n"

                    )



                    if is_higher:


                        answer += (

                            f"현재 {target_bank}보다 "

                            f"높은 금리를 제공하는 은행은 "

                            f"{len(result)}개입니다.\n\n"

                        )


                    else:


                        answer += (

                            f"현재 {target_bank}보다 "

                            f"낮은 금리를 제공하는 은행은 "

                            f"{len(result)}개입니다.\n\n"

                        )



                    # -------------------------------
                    # TOP 10 출력
                    # -------------------------------

                    if result:


                        for idx, item in enumerate(

                            result[:10],

                            start=1

                        ):


                            diff = round(

                                item["rate"]

                                -

                                target_rate,

                                2

                            )



                            if diff > 0:


                                diff_text = (

                                    f'<span class="rate-change increase">'

                                    f'+{diff:.2f}%p'

                                    f'</span>'

                                )


                            else:


                                diff_text = (

                                    f'<span class="rate-change decrease">'

                                    f'▲{abs(diff):.2f}%p'

                                    f'</span>'

                                )



                            answer += (

                                f"{idx}. "

                                f"{item['bank']} "

                                f"{item['rate']:.2f}% "

                                f"({diff_text})\n"

                            )


                    else:


                        answer += (

                            "조건에 맞는 은행이 없습니다."

                        )



                else:


                    answer = (

                        f"{target_bank} 데이터를 찾을 수 없습니다."

                    )



            else:


                answer = (

                    "비교할 은행을 찾을 수 없습니다."

                )

        # -------------------------------
        # 우리금융 시장 순위
        # -------------------------------

        elif (

            "우리금융"

            in question

            and

            "순위"

            in question

        ):


            woori_items = find_bank_products(

                products,

                "우리금융저축은행"

            )


            if woori_items:


                item = max(

                    woori_items,

                    key=lambda x:

                        x["rate"]

                )


                rank = get_market_bank_rank(

                    products,

                    item["bank"]

                )


                answer = (

                    "🏦 우리금융저축은행 시장 순위\n\n"

                    f"기간 : {search_period}\n"

                    f"대표상품 : {item['product']}\n"

                    f"금리 : {item['rate']:.2f}%\n"

                    f"순위 : {rank['rank']}위 / "

                    f"{rank['total']}개사"

                )



        # -------------------------------
        # 일반 검색
        # -------------------------------

        if not answer:


            result = search_product_keyword(

                products,

                question

            )


            if result:


                answer = (

                    f"📌 {search_period} 검색 결과\n\n"

                )


                for item in result[:10]:


                    answer += (

                        f"{item['bank']} "

                        f"{item['product']} "

                        f"{item['rate']:.2f}%\n"

                    )



        # -------------------------------
        # Gemini 전망 분석
        # 단순검색과 분리
        # -------------------------------


        gemini_required = any(

            x in question

            for x in [

                "전망",

                "예측",

                "전략",

                "보고서",

                "시장 전망",

                "금리 전망"

            ]

        )



        if gemini_required:


            try:


                avg_rate = sum(

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



                market_context = {


                    "검색기간":

                        search_period,


                    "상품수":

                        len(products),


                    "평균금리":

                        round(avg_rate,2),


                    "최고금리":

                        highest,


                    "최저금리":

                        lowest,


                    "상품데이터":

                        products[:30]

                }



                market_data = json.dumps(

                    market_context,

                    ensure_ascii=False

                )



                prompt_question = (

                    "당신은 저축은행 예금금리 전략 담당자입니다.\n\n"

                    "현재 금리 데이터를 단순 요약하지 말고 "

                    "시장 전망과 전략 관점으로 분석하세요.\n\n"

                    "반드시 포함:\n"

                    "1. 향후 금리 방향 전망\n"

                    "2. 저축은행 경쟁 변화\n"

                    "3. 고객 유치 전략\n"

                    "4. 우리금융저축은행 대응 방향\n\n"

                    "질문:\n"

                    + question

                )



                ai_comment = ask_gemini(

                    prompt_question,

                    market_data

                )



                if answer:


                    answer += (

                        "\n\n"

                        "🤖 AI 전문가 분석\n\n"

                        + ai_comment

                    )


                else:


                    answer = (

                        "🤖 AI 전문가 분석\n\n"

                        + ai_comment

                    )



            except Exception as e:


                print(

                    "GEMINI ERROR:",

                    e

                )



        if not answer:


            answer = (

                "검색 결과가 없습니다."

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
# Scheduler 연결
# -------------------------------

from scheduler import start_scheduler



# -------------------------------
# 실행
# -------------------------------


if __name__ == "__main__":


    # ===============================
    # 자동 금리 업데이트 스케줄러 시작
    # 매일 00:05 crawler.py 실행
    # ===============================

    start_scheduler()



    # ===============================
    # Flask 서버 실행
    # ===============================

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True,

        use_reloader=False

    )