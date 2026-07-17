# ==========================================
# SBRateBot V4 Scheduler TEST VERSION
# 1분마다 금리 업데이트 테스트
# ==========================================


import os
import subprocess
import sys

from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler



# ==========================================
# 기본 경로
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)



# ==========================================
# 크롤러 실행
# ==========================================

def run_crawler():

    print()

    print("=" * 60)

    print(
        "자동 금리 업데이트 테스트 시작"
    )

    print(
        datetime.now()
    )

    print("=" * 60)



    try:


        crawler_path = os.path.join(

            BASE_DIR,

            "crawler",

            "fsb.py"

        )



        print(
            "실행 파일:",
            crawler_path
        )



        subprocess.run(

            [

                sys.executable,

                crawler_path

            ],

            check=True

        )



        print()

        print(
            "자동 금리 업데이트 테스트 완료"
        )



    except Exception as e:


        print()

        print(
            "자동 업데이트 실패:",
            e
        )



# ==========================================
# Scheduler
# ==========================================

scheduler = BackgroundScheduler(

    timezone="Asia/Seoul"

)



def start_scheduler():



    scheduler.add_job(

        run_crawler,

        "interval",

        minutes=1,

        id="test_rate_update",

        replace_existing=True

    )



    scheduler.start()



    print()

    print(
        "SBRateBot Scheduler 시작"
    )


    print(
        "테스트 업데이트 시간 : 1분마다 실행"
    )