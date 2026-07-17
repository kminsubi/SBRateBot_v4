import os
import json
import shutil
import urllib.parse
import urllib3
import requests
import re
import html as html_module

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

BANK_FILE = os.path.join(
    DATA_DIR,
    "banks.json"
)


# ==========================================
# 중앙회 URL
# ==========================================

RATE_URL = (
    "https://www.fsb.or.kr/"
    "ratcodi_0100_02.jct"
)

BANK_URL = (
    "https://www.fsb.or.kr/"
    "cosfindquic_0100.act"
)


# ==========================================
# 공통 헤더
# ==========================================

COMMON_HEADERS = {

    "Accept":
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,*/*;q=0.8",

    "Accept-Language":
        "ko-KR,ko;q=0.9,en-US;q=0.8",

    "User-Agent":
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/150.0.0.0 "
        "Safari/537.36"

}


# ==========================================
# 은행명 정리
# ==========================================

def clean_bank_name(name):

    name = str(
        name or ""
    ).strip()

    name = html_module.unescape(
        name
    )

    name = re.sub(
        r"<[^>]+>",
        "",
        name
    )

    name = name.replace(
        "(주)",
        ""
    )

    name = name.replace(
        "㈜",
        ""
    )

    name = name.replace(
        "저축은행",
        ""
    )

    name = name.strip()

    return name


# ==========================================
# 전체 저축은행 목록 수집
# ==========================================

def collect_banks():

    print()

    print(
        "전체 저축은행 목록 수집 시작"
    )


    response = requests.get(

        BANK_URL,

        headers=COMMON_HEADERS,

        verify=False,

        timeout=30

    )


    response.raise_for_status()


    response.encoding = (

        response.apparent_encoding

        or

        "utf-8"

    )


    html = response.text


    
    # ======================================
    # HTML 태그 제거
    # ======================================

    text = re.sub(

        r"<script.*?</script>",

        " ",

        html,

        flags=(
            re.IGNORECASE
            |
            re.DOTALL
        )

    )


    text = re.sub(

        r"<style.*?</style>",

        " ",

        text,

        flags=(
            re.IGNORECASE
            |
            re.DOTALL
        )

    )


    text = re.sub(

        r"<[^>]+>",

        "\n",

        text

    )


    text = html_module.unescape(
        text
    )


    text = re.sub(

        r"[ \t]+",

        " ",

        text

    )


        # ======================================
    # 저축은행명 추출
    #
    # HTML 실제 구조 대응
    # ======================================

    matches = re.findall(

        r">\s*([가-힣A-Za-z0-9]+)\s*<",

        text

    )


    banks = {}


    for name in matches:


        bank = clean_bank_name(
            name
        )


        if not bank:

            continue


        # ==================================
        # 잘못 잡히는 일반 단어 제외
        # ==================================

        excluded = {

            "검색결과",
            "전화번호",
            "콜센터",
            "주소",
            "가능",
            "불가능",
            "CD",
            "CDP",
            "ATM",
            "본점",
            "지점",
            "금융센터",
            "영업점",
            "출장소"

        }


        if bank in excluded:

            continue


        if len(bank) > 20:

            continue


        key = (
            bank
            .replace(
                " ",
                ""
            )
            .lower()
        )


        banks[key] = bank


    bank_list = sorted(
        banks.values()
    )


    print(
        "점포 기준 추출 은행 :",
        len(bank_list)
    )


    # ======================================
    # 수집 실패 보호
    # ======================================

    if len(bank_list) < 70:


        print()
        print(
            "추출 은행 목록:"
        )


        for bank in bank_list:

            print(
                "-",
                bank
            )


        raise Exception(

            "전체 저축은행 목록 수집 실패 "
            f"({len(bank_list)}개)"

        )


    # ======================================
    # banks.json 저장
    # ======================================

    with open(

        BANK_FILE,

        "w",

        encoding="utf-8"

    ) as f:


        json.dump(

            bank_list,

            f,

            ensure_ascii=False,

            indent=4

        )


    print(
        "전체 저축은행 :",
        len(bank_list)
    )


    print(
        "은행 목록 저장 완료"
    )


    print(
        BANK_FILE
    )


    return bank_list


# ==========================================
# 금리 요청 데이터
# ==========================================

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


RATE_HEADERS = {

    "Accept": "*/*",

    "Content-Type":
        "application/x-www-form-urlencoded; "
        "charset=UTF-8",

    "Origin":
        "https://www.fsb.or.kr",

    "Referer":
        "https://www.fsb.or.kr/"
        "ratcodi_0100.act",

    "User-Agent":
        "Mozilla/5.0",

    "X-Requested-With":
        "XMLHttpRequest"

}


# ==========================================
# 수집 시작
# ==========================================

print("=" * 70)

print(
    "저축은행 금리 수집 시작"
)

print("=" * 70)


try:


    # ======================================
    # 전체 은행 목록
    # ======================================

    bank_list = collect_banks()


    # ======================================
    # 금리 데이터 수집
    # ======================================

    print()

    print(
        "금리 상품 수집 시작"
    )


    json_text = json.dumps(

        payload,

        separators=(
            ",",
            ":"
        )

    )


    body = {

        "_JSON_":
            urllib.parse.quote(
                json_text
            )

    }


    response = requests.post(

        RATE_URL,

        headers=RATE_HEADERS,

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


    if not isinstance(
        records,
        list
    ):

        raise Exception(
            "REC 데이터 형식 오류"
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
    # 이전 데이터 로드
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


            old_list = json.load(
                f
            )


        if isinstance(
            old_list,
            list
        ):


            for old in old_list:


                if not isinstance(
                    old,
                    dict
                ):

                    continue


                key = (

                    str(
                        old.get(
                            "bank",
                            ""
                        )
                    )

                    +

                    "|"

                    +

                    str(
                        old.get(
                            "product",
                            ""
                        )
                    )

                )


                previous_data[
                    key
                ] = old


    print(
        "이전 비교 상품 :",
        len(previous_data)
    )


    # ======================================
    # 데이터 변환
    # ======================================

    data = []


    for item in records:


        if not isinstance(
            item,
            dict
        ):

            continue


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


            "change_1": 0,

            "change_3": 0,

            "change_6": 0,

            "change_12": 0,

            "change_24": 0,

            "change_36": 0

        }


        # ==================================
        # 전일 대비 계산
        # ==================================

        key = (

            str(
                row["bank"]
            )

            +

            "|"

            +

            str(
                row["product"]
            )

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
                    "top_"
                    +
                    period
                    +
                    "m"
                )


                yesterday = old.get(
                    "top_"
                    +
                    period
                    +
                    "m"
                )


                try:


                    if (

                        today is not None

                        and

                        yesterday is not None

                    ):


                        diff = (

                            float(
                                today
                            )

                            -

                            float(
                                yesterday
                            )

                        )


                        row[

                            "change_"
                            +
                            period

                        ] = round(
                            diff,
                            2
                        )


                except (
                    ValueError,
                    TypeError
                ):

                    pass


        data.append(
            row
        )


    # ======================================
    # latest_rates 저장
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
    # 업데이트 정보
    # ======================================

    update_info = {


        "last_update":

            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),


        "count":
            len(data),


        "bank_count":
            len(bank_list)

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
        update_info[
            "last_update"
        ]
    )


    print(
        "상품 수:",
        update_info[
            "count"
        ]
    )


    print(
        "전체 저축은행 수:",
        update_info[
            "bank_count"
        ]
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