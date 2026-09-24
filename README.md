# Midterm Rental Lead Monitor

Watches public, rule-compliant sources for signs that snowbirds, travel
nurses, construction/disaster-recovery crews, insurance-claim tenants, or
other traveling professionals will need 1-6 month housing in your market —
and uses Claude to read each result and decide whether it's actually
relevant before it ever reaches you.

**What it checks right now:**
- **FEMA disaster declarations** — a storm/flood/fire declaration in your
  county is an early signal that insurance tenants and repair/construction
  crews are coming. No account needed.
- **NWS severe weather alerts** — near-term version of the same signal.
  No account needed.
- **Reddit** (r/TravelNursing, r/Construction, r/snowbirds, etc.) — actual
  people posting about an upcoming housing need. Needs a free Reddit API
  key (instructions below).

**Deliberately NOT included:** Facebook groups and Craigslist. Both
prohibit this kind of automated monitoring in their terms of service, and
doing it anyway risks getting your account banned (Facebook) or a legal
cease-and-desist (Craigslist has sued scrapers before). If you want
coverage there, do it manually or have a VA check periodically — this tool
can still help by drafting replies for you to review and post yourself.

## 1. Install (one-time)

Open Terminal, navigate to this folder, and run:

```bash
pip3 install -r requirements.txt
```

## 2. Add your API keys (one-time)

```bash
cp .env.example .env
```

Then open `.env` in any text editor and fill in:

- **ANTHROPIC_API_KEY** — from https://console.anthropic.com/settings/keys
  (this is what lets the system "read and understand" posts, not just
  keyword-match them)
- **REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET** — go to
  https://www.reddit.com/prefs/apps, click "create app", choose type
  **script**, and put anything in the redirect URI field (e.g.
  `http://localhost:8080`). It'll give you the two values to paste in.
- **SLACK_WEBHOOK_URL** — optional, only if you want leads posted straight
  to a Slack channel.

## 3. Set your market

Open `config.py` and edit the `MARKETS` list at the top — it ships with two
example Florida Gulf Coast markets. Update the state, county name, and NWS
zone code to match where you actually operate. (Look up your NWS zone code
by searching "NWS public zone [your county]".)

## 4. Run it

```bash
python3 main.py
```

Each run checks every source once, prints anything new it found, and saves
it to `leads.db` so you never see the same lead twice. A "market signal"
(FEMA/NWS) means demand is coming to an area, not a specific person to
contact. An "individual lead" (Reddit) is an actual post from someone with a
draft reply suggestion you can copy, tweak, and send yourself.

## 5. Run it automatically (optional)

**Mac/Linux**, via cron — run `crontab -e` and add a line like:

```
0 * * * * cd /path/to/midterm-lead-gen && /usr/bin/python3 main.py >> run.log 2>&1
```

That checks every hour and logs output to `run.log`.

## Extending it

- **More subreddits/keywords:** edit `SUBREDDITS` and `GLOBAL_KEYWORDS` in
  `config.py`.
- **More markets:** add another entry to `MARKETS` in `config.py`.
- **A staffing-agency job board:** each site's HTML is different, so a
  generic scraper isn't reliable — tell me which specific site(s) you want
  (e.g. a specific travel nurse agency's public job board) and I'll write a
  source module for it, checking that site's terms first.
- **Email instead of/in addition to Slack:** ask and I'll add an SMTP
  notifier module.
