import os
import json
import shutil
import urllib.parse
import urllib3
import requests
from datetime import datetime


urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)


# ==========================================
# 경로 설정
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)


os.makedirs(
    DATA_DIR,
    exist_ok=True
)



LATEST_FILE = os.path.join(
    DATA_DIR,
    "latest_rates.json"
)


PREVIOUS_FILE = os.path.join(
    DATA_DIR,
    "previous_rates.json"
)


UPDATE_FILE = os.path.join(
    DATA_DIR,
    "update_info.json"
)



# ==========================================
# 저축은행중앙회 요청 정보
# ==========================================

URL = (
    "https://www.fsb.or.kr/"
    "ratcodi_0100_02.jct"
)



payload = {

    "END_NUM": "100000",

    "START_NUM": "1",

    "DAN": "12",

    "JOIN": "1|2|3|4|5|9",

    "SWECODE": "",

    "ORDERBY": "",

    "SEARCH_SELECT_IN": "",

    "SEARCH_TEXT_IN": "",


    "YN_SEOUL": "1",
    "YN_BUSAN": "1",
    "YN_DEAGU": "1",
    "YN_INCHEON": "1",
    "YN_KWANGJU": "1",
    "YN_DEAJEON": "1",
    "YN_ULSAN": "1",
    "YN_SEJONG": "1",
    "YN_SEONGNAM": "1",
    "YN_KANGWON": "1",
    "YN_CHUNGBUK": "1",
    "YN_CHUNGNAM": "1",
    "YN_JEONBUK": "1",
    "YN_JEONNAM": "1",
    "YN_KYUNGBUK": "1",
    "YN_KYUNGNAM": "1",
    "YN_JEJU": "1"

}



headers = {


    "Accept": "*/*",

    "Content-Type":
        "application/x-www-form-urlencoded; charset=UTF-8",

    "Origin":
        "https://www.fsb.or.kr",

    "Referer":
        "https://www.fsb.or.kr/ratcodi_0100.act",

    "User-Agent":
        "Mozilla/5.0",

    "X-Requested-With":
        "XMLHttpRequest"

}



# ==========================================
# 수집 시작
# ==========================================

print("=" * 70)

print("저축은행 금리 수집 시작")

print("=" * 70)



try:


    json_text = json.dumps(
        payload,
        separators=(",", ":")
    )


    body = {

        "_JSON_":
            urllib.parse.quote(
                json_text
            )

    }


    response = requests.post(

        URL,

        headers=headers,

        data=body,

        verify=False,

        timeout=30

    )


    response.raise_for_status()


    result = response.json()


    records = result.get(
        "REC",
        []
    )


    print(
        "수집 상품 :",
        len(records)
    )


    if len(records) == 0:

        raise Exception(
            "수집 데이터 없음"
        )
    # ======================================
    # 기존 데이터 백업
    # ======================================

    if os.path.exists(
        LATEST_FILE
    ):

        shutil.copy(

            LATEST_FILE,

            PREVIOUS_FILE

        )



    # ======================================
    # 이전 데이터 로딩
    # ======================================

    previous_data = {}


    if os.path.exists(
        PREVIOUS_FILE
    ):


        with open(

            PREVIOUS_FILE,

            "r",

            encoding="utf-8"

        ) as f:


            old_list = json.load(f)



            for old in old_list:


                key = (

                    old.get(
                        "bank",
                        ""
                    )

                    +

                    "|"

                    +

                    old.get(
                        "product",
                        ""
                    )

                )


                previous_data[key] = old





    # ======================================
    # 데이터 변환
    # ======================================


    data = []



    for item in records:


        row = {


            "bank":

                item.get(
                    "KOR_CO_NM",
                    ""
                ),



            "product":

                item.get(
                    "PRODUCT_NAME",
                    ""
                ),



            "top_1m":

                item.get(
                    "TOP_1M_DAN"
                ),



            "top_3m":

                item.get(
                    "TOP_3M_DAN"
                ),



            "top_6m":

                item.get(
                    "TOP_6M_DAN"
                ),



            "top_12m":

                item.get(
                    "TOP_12M_DAN"
                ),



            "top_24m":

                item.get(
                    "TOP_24M_DAN"
                ),



            "top_36m":

                item.get(
                    "TOP_36M_DAN"
                ),



            "base_1m":

                item.get(
                    "JUNG_1M_DAN"
                ),



            "base_3m":

                item.get(
                    "JUNG_3M_DAN"
                ),



            "base_6m":

                item.get(
                    "JUNG_6M_DAN"
                ),



            "base_12m":

                item.get(
                    "JUNG_12M_DAN"
                ),



            "base_24m":

                item.get(
                    "JUNG_24M_DAN"
                ),



            "base_36m":

                item.get(
                    "JUNG_36M_DAN"
                ),



            "reg_date":

                item.get(
                    "REG_DATE"
                ),



            "join_target":

                item.get(
                    "JOIN_TARGET"
                ),



            "sweetener":

                item.get(
                    "SWEETENER"
                ),



            "url":

                item.get(
                    "PRODUCT_URL"
                ),



            "homepage":

                item.get(
                    "URL"
                ),



            "tel":

                item.get(
                    "TEL"
                ),



            "owner":

                item.get(
                    "OWNER"
                ),



            # 전일 대비

            "change_1":

                0,


            "change_3":

                0,


            "change_6":

                0,


            "change_12":

                0,


            "change_24":

                0,


            "change_36":

                0

        }



        # ======================================
        # 전일 대비 금리 변화 계산
        # ======================================


        key = (

            row["bank"]

            +

            "|"

            +

            row["product"]

        )


        old = previous_data.get(
            key
        )



        if old:


            for period in [

                "1",
                "3",
                "6",
                "12",
                "24",
                "36"

            ]:


                today = row.get(
                    "top_" + period + "m"
                )


                yesterday = old.get(
                    "top_" + period + "m"
                )


                try:


                    if (

                        today is not None

                        and

                        yesterday is not None

                    ):


                        diff = (

                            float(today)

                            -

                            float(yesterday)

                        )


                        row[

                            "change_" + period

                        ] = round(

                            diff,

                            2

                        )


                except:


                    pass



        data.append(
            row
        )


    # ======================================
    # latest_rates.json 저장
    # ======================================




    # ======================================
    # 신규 데이터 latest 저장
    # ======================================

    with open(
        LATEST_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )




    # ======================================
    # 업데이트 정보 저장
    # ======================================


    update_info = {


        "last_update":

            datetime.now()
            .strftime(
                "%Y-%m-%d %H:%M:%S"
            ),



        "count":

            len(data)


    }





    with open(

        UPDATE_FILE,

        "w",

        encoding="utf-8"

    ) as f:


        json.dump(

            update_info,

            f,

            ensure_ascii=False,

            indent=4

        )





    print()

    print(
        "JSON 저장 완료"
    )


    print(
        LATEST_FILE
    )


    print()

    print(
        "업데이트 시간:",
        update_info["last_update"]
    )


    print(
        "상품 수:",
        update_info["count"]
    )


    print()

    print(
        "크롤링 완료"
    )





except Exception as e:


    print()

    print(
        "❌ 금리 수집 실패"
    )


    print(
        str(e)
    )


    print(
        "기존 JSON 유지"
    )