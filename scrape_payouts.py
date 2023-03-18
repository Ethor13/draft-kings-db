import pandas as pd
import requests
import concurrent.futures
import json
import os
import sys
import datetime
import random

MAX_WORKERS = 15
DOWNLOAD_DIR = "tmp/downloads/"
CONTESTS_DIR = "contests/"
MAX_ENTRIES_DIR = "max-entries/"
PAYOUTS_DIR = "payouts/"
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36 Edg/89.0.774.76",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
]
details_url = "https://api.draftkings.com/contests/v1/contests/{}?format=json"


def get_url(id, user_agent):
    headers = {"user-agent": user_agent}
    response = requests.get(url=details_url.format(id), headers=headers)
    if response.status_code == 200:
        f = DOWNLOAD_DIR + f"{id}.json"
        json.dump(response.json(), open(f, "w"))
    return response.status_code


def launch(ids):
    # https://zetcode.com/python/concurrent-http-requests/
    k = len(ids)
    print(f"Downloading {k} contest details files")
    user_agents = random.choices(USER_AGENTS, k=k)
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for id, user_agent in zip(ids, user_agents):
            futures.append(executor.submit(get_url, id=id, user_agent=user_agent))

        n = 0
        for future in concurrent.futures.as_completed(futures):
            n += 1
            if future.result() != 200:
                print(f"FAILURE: {id=}", file=sys.stderr, flush=True)
            if n % 100 == 0:
                print(n, end=", ", flush=True)


if __name__ == "__main__":
    today = datetime.datetime.today().strftime("%m-%d-%Y")

    # Catch up on missed contests
    # available_contest_dates = os.listdir(CONTESTS_DIR)
    # today = None
    # idx = 0
    # while today is None:
    #     d = available_contest_dates[idx]
    #     if not os.path.exists(PAYOUTS_DIR + d):
    #         today = d.split(".")[0]
    #     idx += 1
    #     if idx == len(available_contest_dates):
    #         break

    # if today is None:
    #     print("all up to date on payouts")
    #     exit(0)
    # else:
    #     print(f"Scraping {today}")

    contests_path = CONTESTS_DIR + f"{today}.csv"
    if not os.path.exists(contests_path):
        print("No contests from today to scrape payouts for")
        exit(0)

    ct_df = pd.read_csv(contests_path, index_col="contest_id")

    os.makedirs(DOWNLOAD_DIR)

    # Download everything
    launch(ct_df.index)

    # Parse Downloads and Update existing CSVs
    max_entries = pd.DataFrame([], index=ct_df.index, columns=["entry_max_per_user"])
    payouts = []
    for contest_id in ct_df.index:
        f = DOWNLOAD_DIR + f"{contest_id}.json"
        if not os.path.exists(f):
            continue
        obj = json.load(open(f, "r"))
        for tier in obj["contestDetail"]["payoutSummary"]:
            try:
                payout = [
                    contest_id,
                    tier["minPosition"],
                    tier["maxPosition"],
                    sum(
                        list(
                            map(
                                lambda payout: payout.get("quantity", 0)
                                * payout.get("value", 0),
                                tier.get("payoutDescriptions", {}),
                            )
                        )
                    ),
                ]
                payouts.append(payout)
            except KeyError as e:
                print(f, e, file=sys.stderr)
                exit(1)

        max_entries.loc[contest_id, "entry_max_per_user"] = obj["contestDetail"][
            "maximumEntriesPerUser"
        ]
    max_entries.to_csv(MAX_ENTRIES_DIR + f"{today}.csv")

    pay_cols = ["contest_id", "minPosition", "maxPosition", "payout"]
    pay_df = pd.DataFrame(payouts, columns=pay_cols)
    pay_df.set_index("contest_id", drop=True, inplace=True)
    pay_df.to_csv(PAYOUTS_DIR + f"{today}.csv")

    # Clear downloads directory
    for f in os.listdir(DOWNLOAD_DIR):
        os.remove(DOWNLOAD_DIR + f)
    os.rmdir(DOWNLOAD_DIR)
