import pandas as pd
from pandas.errors import EmptyDataError
from datetime import datetime
from datetime import timedelta
import os

if __name__ == "__main__":
    two_days_ago = datetime.today() - timedelta(days=2)
    date_dir = two_days_ago.strftime("%m-%d-%Y") + "/"
    os.makedirs("standings/" + date_dir, exist_ok=True)
    os.makedirs("player-performances/" + date_dir, exist_ok=True)

    for f in os.listdir("tmp/downloads/"):
        contest_id = f.split("-")[-1][:-4]
        try:
            df = pd.read_csv("tmp/downloads/" + f, dtype={"EntryId": object})

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
                "T\d+",
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
            standings.to_csv("standings/" + f, index=False)
            player_performances.to_csv("player-performances/" + f, index=False)

        except EmptyDataError as e:
            pass

    exit(0)
