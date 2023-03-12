import csv
import math
import os
import datetime
import sys

ROWS_PER_FILE = 50
standings_url = "https://draftkings.com/contest/exportfullstandingscsv/"

if __name__ == "__main__":
    two_days_ago = datetime.datetime.today() - datetime.timedelta(days=2)

    fname = f"contests/{two_days_ago.strftime('%m-%d-%Y')}.csv"
    if os.path.exists(fname):
        contest_urls = []
        with open(fname, "r") as f:
            reader = csv.reader(f)
            # skip headers
            next(reader)
            for line in reader:
                contest_urls.append([standings_url + str(line[0])])

        os.makedirs("tmp/urls/", exist_ok=True)
        for i in range(math.ceil(len(contest_urls) / ROWS_PER_FILE)):
            with open(f"tmp/urls/url_batch_{i + 1}.txt", "w", newline="") as f:
                writer = csv.writer(f, lineterminator="\n")
                start_file_num = i * ROWS_PER_FILE
                end_file_num = (i + 1) * ROWS_PER_FILE
                writer.writerows(contest_urls[start_file_num:end_file_num])

        print("Wrote URLs successfully in the tmp/urls folder")
        exit(0)

    else:
        print("Could not find contests from two days ago", file=sys.stderr)
        exit(1)
