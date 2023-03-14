#!/bin/bash
mkdir tmp
python scrape_contests.py && \
python scrape_payouts.py
python scripts/python/get_urls.py && \
python scripts/python/selenium_scraper.py && \
./scripts/shell/download_standings.sh && \
./scripts/shell/format_standings.sh && \
python scripts/python/parse_csvs.py
rm -rf tmp