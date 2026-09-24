"""
Where new leads get announced. Always prints to the console; optionally also
posts to a Slack channel if SLACK_WEBHOOK_URL is set in .env.
"""
import os
import requests


def announce(new_items):
    if not new_items:
        print("No new leads/signals this run.")
        return

    print(f"\n{len(new_items)} new lead(s)/signal(s) found:\n")
    for item in new_items:
        print("-" * 70)
        print(f"[{item.get('kind')}] {item.get('segment', '').upper() or item['source']}")
        print(f"Title:     {item['title']}")
        if item.get("location"):
            print(f"Location:  {item['location']}")
        if item.get("timeframe"):
            print(f"Timeframe: {item['timeframe']}")
        print(f"Summary:   {item.get('summary', '')}")
        if item.get("suggested_reply"):
            print(f"Suggested reply: {item['suggested_reply']}")
        print(f"Link:      {item.get('url')}")
    print("-" * 70 + "\n")

    webhook = os.getenv("SLACK_WEBHOOK_URL")
    if webhook:
        text = "\n\n".join(
            f"*{i.get('segment', i['source'])}* — {i['title']}\n{i.get('summary','')}\n{i.get('url','')}"
            for i in new_items
        )
        try:
            requests.post(webhook, json={"text": text}, timeout=10)
        except requests.RequestException as e:
            print(f"[notifier] Slack post failed: {e}")
