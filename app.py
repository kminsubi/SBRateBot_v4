from flask import Flask, render_template, jsonify
import json
import os


app = Flask(__name__)


# ===================================
# JSON 데이터 로드
# ===================================

def load_rates():

    file_path = os.path.join(
        "data",
        "latest_rates.json"
    )

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)





# ===================================
# Dashboard
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

    data = load_rates()

    market = data["market"]


    return jsonify({

        "product_count":
            market["product_count"],

        "max_rate":
            f'{market["max_rate"]:.2f}%',


        "average_rate":
            f'{market["average_rate"]:.2f}%',


        "min_rate":
            f'{market["min_rate"]:.2f}%',


        "daily_change":
            market["daily_change"]

    })







# ===================================
# 우리금융 Market Position
# ===================================

@app.route("/api/woori")
def api_woori():

    data = load_rates()


    return jsonify(

        data["woori"]

    )







# ===================================
# 시장 TOP10
# ===================================

@app.route("/api/rates")
def api_rates():

    data = load_rates()


    return jsonify(

        data["top10"]

    )







# ===================================
# 금융지주 저축은행 비교
# ===================================

@app.route("/api/financial")
def api_financial():

    data = load_rates()


    return jsonify(

        data["financial_savings"]

    )







# ===================================
# 전체 상품 조회
# ===================================

@app.route("/api/products")
def api_products():

    data = load_rates()


    return jsonify(

        data["products"]

    )







# ===================================
# AI Summary
# ===================================

@app.route("/api/ai")
def api_ai():

    data = load_rates()


    return jsonify({

        "summary":
            data["ai_summary"]

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