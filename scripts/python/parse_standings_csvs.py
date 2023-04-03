import pandas as pd
from pandas.errors import EmptyDataError
from datetime import datetime
from datetime import timedelta
import os

DOWNLOAD_DIR = "tmp/downloads/"
STANDINGS_DIR = "standings/"
PERFORMANCE_DIR = "player-performances/"

if __name__ == "__main__":
    two_days_ago = datetime.today() - timedelta(days=2)
    date_dir = two_days_ago.strftime("%m-%d-%Y") + "/"

    # Catch up on missed contests
    available_contest_dates = os.listdir("contests/")
    two_days_ago = None
    idx = 0
    while two_days_ago is None:
        d = available_contest_dates[idx].split(".")[0]
        if not os.path.exists("standings/" + d):
            two_days_ago = d
        idx += 1
        if idx == len(available_contest_dates):
            break

    if two_days_ago is None:
        print("Don't know where to write files")
        exit(0)
    else:
        print(f"Making new folder: {two_days_ago}")
    date_dir = two_days_ago + "/"

    os.makedirs(STANDINGS_DIR + date_dir, exist_ok=True)
    os.makedirs(PERFORMANCE_DIR + date_dir, exist_ok=True)

    successes = 0
    errors = 0
    for f in os.listdir(DOWNLOAD_DIR):
        contest_id = f.split("-")[-1][:-4]
        try:
            df = pd.read_csv(DOWNLOAD_DIR + f, dtype={"EntryId": object})

            standings = df.loc[:, "EntryName"].str.replace(")", "", regex=False)
            standings = standings.str.split("\s\(|/", expand=True).fillna(1)
            if len(standings.columns) < 3:
                standings[["EntryNumber", "EntryTotal"]] = 1
            standings.columns = ["Username", "EntryNumber", "EntryTotal"]
            standings.insert(0, "EntryId", df.loc[:, "EntryId"])
            standings.insert(len(standings.columns), "Points", df.loc[:, "Points"])

            positions = [
                "PG",
                "SG",
                "SF",
                "PF",
                "C",
                "G",
                "F",
                "UTIL",
                "CPT",
                "BENCH",
                "F/C",
                "T\d+",  # Matches Tiers positions (T1, T2, T3, ...)
            ]
            position_regex = r"\b({})\s".format("|".join(positions))
            lineups_raw = df.Lineup.str.split(position_regex, expand=True)
            vals = lineups_raw.iloc[:, 2::2].values
            cols = lineups_raw.iloc[0, 1::2].values
            lineups = pd.DataFrame(vals, columns=cols)
            lineups = lineups.apply(lambda col: col.str.strip())

            standings = pd.concat([standings, lineups], axis=1)
            standings = standings.dropna(axis=0, how="any")
            player_performances = df.iloc[:, 7:].dropna(axis=0, how="all")

            f = date_dir + contest_id + ".csv"
            standings.to_csv(STANDINGS_DIR + f, index=False)
            player_performances.to_csv(PERFORMANCE_DIR + f, index=False)
            successes += 1

        except EmptyDataError as e:
            errors += 1
            pass

    print(f"{successes=}, {errors=}")
    print("Succesfully parsed CSVs")
    exit(0)
