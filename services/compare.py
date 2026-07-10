import json
import os


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


LATEST_FILE = os.path.join(
    BASE_DIR,
    "data",
    "latest_rates.json"
)


PREVIOUS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "previous_rates.json"
)



def load_json(path):

    if not os.path.exists(path):
        return []

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except:

        return []




def make_key(item):

    return (

        item.get("bank", ""),

        item.get("product", "")

    )




def compare_rates():


    latest = load_json(
        LATEST_FILE
    )


    previous = load_json(
        PREVIOUS_FILE
    )


    print(
        "latest 개수:",
        len(latest)
    )


    print(
        "previous 개수:",
        len(previous)
    )



    prev_dict = {}



    for row in previous:

        prev_dict[
            make_key(row)
        ] = row




    # =====================================
    # 전일 대비 계산
    # =====================================

    for row in latest:


        prev = prev_dict.get(
            make_key(row)
        )


        for month in [
            "12",
            "24",
            "36"
        ]:


            current = row.get(
                f"top_{month}m"
            )


            before = None


            if prev:

                before = prev.get(
                    f"top_{month}m"
                )



            try:

                current = float(current)

            except:

                current = None



            try:

                before = float(before)

            except:

                before = None




            if current is None or before is None:

                row[f"change_{month}"] = 0

                continue



            row[f"change_{month}"] = round(
                current - before,
                2
            )




 



    up = []

    down = []



    for row in latest:


        change = row.get(
            "change_12",
            0
        )


        try:

            change = float(change)

        except:

            continue



        data = {

            "bank":
                row.get("bank",""),


            "product":
                row.get("product",""),


            "rate":
                row.get("top_12m",""),


            "change":
                change

        }



        if change > 0:

            up.append(data)



        elif change < 0:

            down.append(data)




    print(
        "상승 개수:",
        len(up)
    )


    print(
        "하락 개수:",
        len(down)
    )



    return latest