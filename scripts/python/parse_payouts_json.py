import pandas as pd
import json
import os
import sys
import datetime

TEMP_DIR = "tmp/"
LOG_DIR = "logs/"
DOWNLOAD_DIR = "tmp/downloads/"
CONTESTS_DIR = "contests/"
MAX_ENTRIES_DIR = "max-entries/"
PAYOUTS_DIR = "payouts/"

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

    # Parse Downloads and Update existing CSVs
    max_entries = pd.DataFrame([], index=ct_df.index, columns=["entry_max_per_user"])
    payouts = []
    for contest_id in ct_df.index:
        f = DOWNLOAD_DIR + f"{contest_id}@format=json"
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
    # remove payouts.log
    if os.path.exists(LOG_DIR + "payouts.log"):
        os.remove(LOG_DIR + "payouts.log")
    # remove flags.csv
    if os.path.exists(TEMP_DIR + "flags.csv"):
        os.remove(TEMP_DIR + "flags.csv")

    exit(0)
