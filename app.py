from flask import Flask, render_template, jsonify, request
import json
import os


app = Flask(__name__)


# ===================================
# 기본 설정
# ===================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


DATA_FILE = os.path.join(
    BASE_DIR,
    "data",
    "latest_rates.json"
)



# ===================================
# 기준 설정
# ===================================

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



# ===================================
# 데이터 로드
# ===================================

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




# ===================================
# 숫자 변환
# ===================================

def safe_float(value):


    try:

        if value in [

            None,

            "",

            "-"

        ]:

            return None


        return float(value)


    except:


        return None




# ===================================
# 문자열 정규화
# ===================================

def normalize(text):


    return (

        str(text or "")

        .replace(

            "(주)",

            ""

        )

        .replace(

            "㈜",

            ""

        )

        .replace(

            "저축은행",

            ""

        )

        .replace(

            "은행",

            ""

        )

        .replace(

            " ",

            ""

        )

        .lower()

    )




# ===================================
# 상품 데이터 생성
# ===================================

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



        if rate is None:

            rate = 0



        change = safe_float(

            item.get(

                change_field

            )

        )


        if change is None:

            change = 0



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

                    "reg_date"

                )


        })


    return products
    # ===================================
# 중복 제거
# ===================================

def unique_products(products):


    result = []

    seen = set()



    for item in products:


        key = (

            item.get("bank"),

            item.get("product"),

            item.get("period")

        )


        if key in seen:

            continue


        seen.add(key)

        result.append(item)



    return result




# ===================================
# 은행 상품 검색
# ===================================

def find_bank_products(

    products,

    keyword

):


    keyword = normalize(keyword)


    result = []



    for item in products:


        bank = normalize(

            item.get("bank")

        )


        if keyword in bank:

            result.append(item)



    return result




# ===================================
# 은행별 최고금리 상품
# ===================================

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




# ===================================
# 시장 순위 계산
# 금리 없는 은행은 제외하지 않고
# 하위 순위 처리 가능하도록 구조 유지
# ===================================

def get_market_bank_rank(

    products,

    target_bank

):


    bank_best = get_bank_best_rates(

        products

    )


    bank_best.sort(

        key=lambda x:

        x["rate"],

        reverse=True

    )



    rank = len(bank_best)



    target = normalize(

        target_bank

    )



    for idx, item in enumerate(

        bank_best,

        start=1

    ):


        if normalize(

            item["bank"]

        ) == target:


            rank = idx

            break



    return {


        "rank":

            rank,


        "total":

            len(bank_best)

    }




# ===================================
# 메인 페이지
# ===================================

@app.route("/")

def index():


    return render_template(

        "index.html"

    )




# ===================================
# KPI
# ===================================

@app.route("/api/kpi")

def api_kpi():


    products = unique_products(

        build_products(

            "12개월"

        )

    )



    rates = [

        x["rate"]

        for x in products

    ]



    if not rates:


        return jsonify({


            "product_count":

                0,


            "max_rate":

                "0.00%",


            "min_rate":

                "0.00%",


            "average_rate":

                "0.00%"


        })



    return jsonify({


        "product_count":

            len(products),


        "max_rate":

            f"{max(rates):.2f}%",


        "min_rate":

            f"{min(rates):.2f}%",


        "average_rate":

            f"{sum(rates)/len(rates):.2f}%"

    })




# ===================================
# 우리금융 Market Position
# ===================================

@app.route("/api/woori")

def api_woori():


    products = unique_products(

        build_products(

            "12개월"

        )

    )



    woori_products = find_bank_products(

        products,

        "우리금융"

    )



    if not woori_products:


        return jsonify({})


    woori = max(

        woori_products,

        key=lambda x:

        x["rate"]

    )



    rank = get_market_bank_rank(

        products,

        woori["bank"]

    )



    rates = [

        x["rate"]

        for x in products

    ]



    avg = sum(rates) / len(rates)



    financial_rank = 0



    financial_products = []



    for bank in FINANCIAL_BANKS:


        temp = find_bank_products(

            products,

            bank

        )


        if temp:


            financial_products.append(

                max(

                    temp,

                    key=lambda x:

                    x["rate"]

                )

            )



    financial_products.sort(

        key=lambda x:

        x["rate"],

        reverse=True

    )



    for idx,item in enumerate(

        financial_products,

        start=1

    ):


        if normalize(

            item["bank"]

        ) == normalize(

            woori["bank"]

        ):


            financial_rank = idx



    return jsonify({


        "bank":

            woori["bank"],


        "basis_product":

            woori["product"],


        "rate":

            woori["rate"],


        "market_rank":

            rank["rank"],


        "bank_count":

            rank["total"],


        "financial_rank":

            financial_rank,


        "average_gap":

            round(

                woori["rate"] - avg,

                2

            ),


        "highest_gap":

            round(

                woori["rate"] - max(rates),

                2

            ),


        "lowest_gap":

            round(

                woori["rate"] - min(rates),

                2

            )

    })
    # ===================================
# 시장 TOP10
# ===================================

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


    bank_best.sort(

        key=lambda x:

        x["rate"],

        reverse=True

    )


    result = []



    for idx, item in enumerate(

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
# 금융지주 저축은행 비교
# ===================================

@app.route("/api/financial")

def api_financial():


    products = unique_products(

        build_products(

            "12개월"

        )

    )


    result = []



    for bank in FINANCIAL_BANKS:


        bank_products = find_bank_products(

            products,

            bank

        )


        if bank_products:


            result.append(

                max(

                    bank_products,

                    key=lambda x:

                    x["rate"]

                )

            )



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





# ===================================
# 전체상품 조회
# ===================================

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

        key=lambda x:(

            x["period"],

            -x["rate"]

        )

    )


    return jsonify(products)





# ===================================
# AI 시장 요약
# ===================================

@app.route("/api/ai")

def api_ai():


    products = unique_products(

        build_products(

            "12개월"

        )

    )


    if not products:


        return jsonify({

            "summary":

                [

                    "금리 데이터가 없습니다."

                ]

        })



    products.sort(

        key=lambda x:

        x["rate"],

        reverse=True

    )



    highest = products[0]

    lowest = products[-1]



    average = sum(

        x["rate"]

        for x in products

    ) / len(products)



    return jsonify({


        "summary":

        [

            f"12개월 최고금리는 {highest['bank']} {highest['product']} {highest['rate']:.2f}%입니다.",

            f"12개월 최저금리는 {lowest['bank']} {lowest['product']} {lowest['rate']:.2f}%입니다.",

            f"12개월 평균금리는 {average:.2f}%입니다."

        ]

    })





# ===================================
# AI 검색
# ===================================

@app.route(

    "/api/ai/search",

    methods=["POST"]

)

def api_ai_search():


    body = request.get_json(

        silent=True

    ) or {}



    question = str(

        body.get(

            "question",

            ""

        )

        or ""

    ).strip()



    products = unique_products(

        build_products(

            "12개월"

        )

    )



    if not products:


        return jsonify({

            "answer":

                "검색 가능한 금리 데이터가 없습니다."

        })



    products.sort(

        key=lambda x:

        x["rate"],

        reverse=True

    )



    q = normalize(question)



    answer = "검색 결과가 없습니다."



    if "최고" in question or "높은" in q:


        item = products[0]


        answer = (

            f"현재 12개월 최고금리는\n\n"

            f"{item['bank']} {item['product']}\n"

            f"{item['rate']:.2f}% 입니다."

        )



    elif "최저" in question or "낮은" in q:


        item = products[-1]


        answer = (

            f"현재 12개월 최저금리는\n\n"

            f"{item['bank']} {item['product']}\n"

            f"{item['rate']:.2f}% 입니다."

        )



    elif "평균" in question:


        avg = sum(

            x["rate"]

            for x in products

        ) / len(products)



        answer = (

            f"현재 12개월 평균금리는\n\n"

            f"{avg:.2f}% 입니다."

        )



    else:


        matches = []



        for item in products:


            if (

                q in normalize(item["bank"])

                or

                q in normalize(item["product"])

            ):


                matches.append(item)



        if matches:


            lines = []


            for item in matches[:5]:


                lines.append(

                    f"{item['bank']} "

                    f"{item['product']} "

                    f"{item['rate']:.2f}%"

                )


            answer = "\n".join(lines)



    return jsonify({

        "answer":

            answer

    })





# ===================================
# 실행
# ===================================

if __name__ == "__main__":


    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )