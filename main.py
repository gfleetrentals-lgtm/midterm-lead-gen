"""
Run this file to do one full pass: check every source, classify what it
finds, save anything new, and print/notify.

    python main.py

To run continuously, use your computer's task scheduler (see README) rather
than a Python sleep loop — that survives reboots and is easier to monitor.
"""
from dotenv import load_dotenv
load_dotenv()

import config
from sources import fema, nws, reddit
import classifier
import storage
import notifier


def run():
    print("Checking market signals (FEMA, NWS)...")
    raw_items = []
    raw_items += fema.fetch(config.MARKETS, lookback_days=config.LOOKBACK_DAYS)
    raw_items += nws.fetch(config.MARKETS)

    print("Checking Reddit for individual leads...")
    raw_items += reddit.fetch(
        config.MARKETS, config.SUBREDDITS, config.GLOBAL_KEYWORDS,
        lookback_days=config.LOOKBACK_DAYS,
    )

    print(f"Found {len(raw_items)} raw item(s). Classifying with Claude...")
    classified = []
    for item in raw_items:
        result = classifier.classify(item)
        if result:
            classified.append(result)

    conn = storage.connect(config.DB_PATH)
    new_items = storage.save_new(conn, classified)

    notifier.announce(new_items)


if __name__ == "__main__":
    run()
