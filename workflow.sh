#!/bin/bash
mkdir tmp

# download contests
{ 
    python scripts/python/scrape_contests.py && \
    echo "Successfully scraped contests"
} || {
    echo "No contests to scrape today"
}

# download payouts
{
    python scripts/python/get_payouts_urls.py && \
    ./scripts/shell/download_payouts.sh && \
    python scripts/python/parse_payouts_json.py && \
    echo "Successfully scraped payouts"
} || {
    echo "No contests to scrape today"
}

# download standings
{
    python scripts/python/get_standings_urls.py && \
    # python scripts/python/selenium_scraper.py && \
    python scripts/python/playwright_scraper.py && \
    ./scripts/shell/download_standings.sh && \
    ./scripts/shell/format_standings.sh && \
    python scripts/python/parse_standings_csvs.py && \
    echo "Successfully scraped standings"
} || {
    echo "No contests from two days ago"
}

rm -rf tmp