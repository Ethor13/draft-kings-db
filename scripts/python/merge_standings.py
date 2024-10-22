import pandas as pd
from pathlib import Path

STANDINGS_DIR = Path("C:/Users/ethor/OneDrive/Data/draft-kings-db/standings")
OUTPUT_DIR = Path("D:/draft-kings-db/standings")
COLS = ["EntryId", "Username", "EntryNumber", "EntryTotal", "Points"]

for date_dir in STANDINGS_DIR.iterdir():
    contests = list(date_dir.iterdir())
    contest_ids = list(map(lambda f: f.stem, contests))

    standings = [pd.read_csv(f, usecols=COLS, index_col="EntryId") for f in contests]
    all_standings = pd.concat(standings, keys=contest_ids, names=["contest_id"])
    all_standings.to_csv(OUTPUT_DIR / f"{date_dir.stem}.csv")
