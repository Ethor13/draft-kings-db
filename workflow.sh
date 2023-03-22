#!/bin/bash
mkdir tmp
# download contests
python scripts/python/scrape_contests.py

# download payouts
python scripts/python/get_payouts_urls.py && \
./scripts/shell/download_payouts.sh && \
python scripts/python/parse_payouts_json.py

# download standings
python scripts/python/get_standings_urls.py && \
python scripts/python/selenium_scraper.py && \ # get cookies for wget
./scripts/shell/download_standings.sh && \
./scripts/shell/format_standings.sh && \
python scripts/python/parse_standings_csvs.py
rm -rf tmp