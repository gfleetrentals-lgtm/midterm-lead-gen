"""
Tiny SQLite store so re-running the monitor doesn't show you the same lead
twice, and so you have one place (leads.db) to look back through everything
found so far. Any SQLite browser (e.g. DB Browser for SQLite, a free app)
can open this file if you want a spreadsheet-like view.
"""
import sqlite3
import hashlib
import datetime

SCHEMA = """
CREATE TABLE IF NOT EXISTS leads (
    id TEXT PRIMARY KEY,
    source TEXT,
    kind TEXT,
    segment TEXT,
    market TEXT,
    location TEXT,
    timeframe TEXT,
    confidence TEXT,
    title TEXT,
    summary TEXT,
    suggested_reply TEXT,
    url TEXT,
    posted_at TEXT,
    found_at TEXT,
    notified INTEGER DEFAULT 0
);
"""


def _make_id(item):
    key = (item.get("url") or item["title"]) + item["source"]
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def connect(db_path):
    conn = sqlite3.connect(db_path)
    conn.execute(SCHEMA)
    conn.commit()
    return conn


def save_new(conn, items):
    """Insert items not already in the DB. Returns the list actually inserted."""
    new_items = []
    for item in items:
        item_id = _make_id(item)
        try:
            conn.execute(
                """INSERT INTO leads
                   (id, source, kind, segment, market, location, timeframe,
                    confidence, title, summary, suggested_reply, url,
                    posted_at, found_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    item_id, item.get("source"), item.get("kind"),
                    item.get("segment"), item.get("market"), item.get("location"),
                    item.get("timeframe"), item.get("confidence"), item.get("title"),
                    item.get("summary"), item.get("suggested_reply"), item.get("url"),
                    item.get("posted_at"), datetime.datetime.utcnow().isoformat(),
                ),
            )
            new_items.append(item)
        except sqlite3.IntegrityError:
            continue  # already seen this one
    conn.commit()
    return new_items
