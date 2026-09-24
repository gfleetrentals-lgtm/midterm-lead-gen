"""
Reddit search = individual-level leads: real people posting about an actual
upcoming housing need. Uses Reddit's official API (PRAW), which requires
your own free API credentials — see README for how to get them.
"""
import os
import datetime

try:
    import praw
except ImportError:
    praw = None


def fetch(markets, subreddits, global_keywords, lookback_days=30):
    """Search configured subreddits for posts matching market/keyword terms."""
    if praw is None:
        print("[reddit] praw not installed — run: pip install praw")
        return []

    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT", "midterm-rental-lead-monitor by u/yourusername")

    if not client_id or not client_secret:
        print("[reddit] missing REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET in .env — skipping")
        return []

    reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)

    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=lookback_days)
    all_keywords = set(global_keywords)
    for m in markets:
        all_keywords.update(m.get("reddit_keywords", []))

    query = " OR ".join(f'"{kw}"' for kw in all_keywords)

    leads = []
    seen_ids = set()
    for sub_name in subreddits:
        try:
            subreddit = reddit.subreddit(sub_name)
            for submission in subreddit.search(query, sort="new", time_filter="month", limit=50):
                if submission.id in seen_ids:
                    continue
                seen_ids.add(submission.id)

                posted = datetime.datetime.utcfromtimestamp(submission.created_utc)
                if posted < cutoff:
                    continue

                leads.append({
                    "source": f"Reddit r/{sub_name}",
                    "market": None,  # classifier will infer/confirm location
                    "title": submission.title,
                    "text": (submission.title + "\n\n" + (submission.selftext or ""))[:2000],
                    "url": f"https://reddit.com{submission.permalink}",
                    "posted_at": posted.isoformat(),
                    "kind": "individual_lead",
                })
        except Exception as e:
            print(f"[reddit] search failed for r/{sub_name}: {e}")

    return leads
