#!/bin/bash
mkdir tmp

# download contests
python scripts/python/scrape_contests.py

# download payouts
if python scripts/python/get_payouts_urls.py; then 
    ./scripts/shell/download_payouts.sh && \
     python scripts/python/parse_payouts_json.py
fi

# download standings
if python scripts/python/get_standings_urls.py; then
    python scripts/python/selenium_scraper.py && \
    ./scripts/shell/download_standings.sh && \
    ./scripts/shell/format_standings.sh && \
    python scripts/python/parse_standings_csvs.py
fi

rm -rf tmp