import csv
import math
import os
import datetime
import sys

ROWS_PER_FILE = 50
URL_DIR = "tmp/urls/"
CONTESTS_DIR = "contests/"
standings_url = "https://draftkings.com/contest/exportfullstandingscsv/"

if __name__ == "__main__":
    two_days_ago = datetime.datetime.today() - datetime.timedelta(days=2)
    fname = CONTESTS_DIR + f"{two_days_ago.strftime('%m-%d-%Y')}.csv"

    # Catch up on missed contests
    # available_contest_dates = os.listdir(CONTESTS_DIR)
    # two_days_ago = None
    # idx = 0
    # while two_days_ago is None:
    #     d = available_contest_dates[idx].split(".")[0]
    #     if not os.path.exists("standings/" + d):
    #         two_days_ago = d
    #     idx += 1
    #     if idx == len(available_contest_dates):
    #         break

    # if two_days_ago is None:
    #     print("all up to date on payouts")
    #     exit(2)
    # else:
    #     print(f"Scraping {two_days_ago}")
    # fname = CONTESTS_DIR + f"{two_days_ago}.csv"

    if os.path.exists(fname):
        contest_urls = []
        with open(fname, "r") as f:
            reader = csv.reader(f)
            # skip headers
            next(reader)
            for line in reader:
                contest_urls.append([standings_url + str(line[0])])

        if os.path.exists(URL_DIR):
            for f in os.listdir(URL_DIR):
                os.remove(URL_DIR + f)
            os.rmdir(URL_DIR)
        os.makedirs(URL_DIR)

        for i in range(math.ceil(len(contest_urls) / ROWS_PER_FILE)):
            with open(URL_DIR + f"url_batch_{i + 1}.txt", "w", newline="") as f:
                writer = csv.writer(f, lineterminator="\n")
                start_file_num = i * ROWS_PER_FILE
                end_file_num = (i + 1) * ROWS_PER_FILE
                writer.writerows(contest_urls[start_file_num:end_file_num])

        print("Wrote URLs successfully in the tmp/urls folder")
        exit(0)

    else:
        print("No contests from two days ago", file=sys.stderr)
        exit(2)
