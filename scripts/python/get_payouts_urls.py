import pandas as pd
import os
import datetime
import random

TEMP_DIR = "tmp/"
LOG_DIR = "logs/"
CONTESTS_DIR = "data/contests/"
PAYOUTS_DIR = "data/payouts/"
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
DETAILS_URL = "https://api.draftkings.com/contests/v1/contests/{}?format=json"

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
        exit(2)

    ct_df = pd.read_csv(contests_path, index_col="contest_id")

    os.makedirs(TEMP_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)

    # TODO: start experimental

    urls = ct_df.index.map(DETAILS_URL.format)
    random_user_agents = random.choices(USER_AGENTS, k=len(urls))
    flag_df = pd.DataFrame([random_user_agents, urls]).T
    flag_df.to_csv(
        TEMP_DIR + "flags.csv",
        index=False,
        header=False,
        sep=" ",
        quoting=1,
        lineterminator="\n",
    )
    print("Successfully wrote flags to tmp/flags.csv")
    exit(0)
