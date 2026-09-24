"""
Uses Claude to read a raw post/listing and decide:
  - is this actually a midterm-rental lead (or market signal)?
  - which segment (snowbird / travel nurse / construction crew / insurance
    claim tenant / other traveling professional)?
  - what location + timeframe does it mention?
This is what lets the system understand phrasing, not just match keywords.
"""
import os
import json

try:
    import anthropic
except ImportError:
    anthropic = None

from config import CLASSIFIER_MODEL

SYSTEM_PROMPT = """You screen posts for a company that rents furnished homes \
on 30-90 day terms in beach vacation markets to: snowbirds, travel nurses, \
construction/disaster-recovery crews, insurance-claim (displaced) tenants, \
and other traveling professionals.

Given one post/listing, decide if it is relevant. Respond with ONLY a JSON \
object, no other text:

{
  "is_relevant": true|false,
  "segment": "snowbird|travel_nurse|construction_crew|insurance_tenant|other_traveling_professional|unclear",
  "location": "string or null",
  "timeframe": "string or null, e.g. '3 months starting June'",
  "confidence": "high|medium|low",
  "one_line_summary": "short human-readable summary of why this is/isn't a lead",
  "suggested_reply": "a short, non-salesy, helpful draft reply IF is_relevant is true and this looks like an individual post you could reply to. null otherwise."
}

Be conservative: market-wide signals (disaster declarations, storm alerts) \
are relevant but have no individual to reply to, so suggested_reply should \
be null for those. Do not mark something relevant just because it mentions \
a beach town in passing — it needs an actual housing/relocation need.
"""


def classify(item):
    """item: dict with title/text/source/kind. Returns enriched dict or None."""
    if anthropic is None:
        print("[classifier] anthropic package not installed — run: pip install anthropic")
        return None

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("[classifier] missing ANTHROPIC_API_KEY in .env — skipping classification")
        return None

    client = anthropic.Anthropic(api_key=api_key)

    user_content = (
        f"Source: {item['source']}\n"
        f"Kind: {item.get('kind')}\n"
        f"Title: {item['title']}\n"
        f"Text: {item['text']}"
    )

    try:
        resp = client.messages.create(
            model=CLASSIFIER_MODEL,
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
        )
        raw = resp.content[0].text.strip()
        # Model sometimes wraps JSON in a code fence despite instructions.
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        result = json.loads(raw)
    except Exception as e:
        print(f"[classifier] failed on '{item['title'][:60]}': {e}")
        return None

    if not result.get("is_relevant"):
        return None

    item.update({
        "segment": result.get("segment"),
        "location": result.get("location"),
        "timeframe": result.get("timeframe"),
        "confidence": result.get("confidence"),
        "summary": result.get("one_line_summary"),
        "suggested_reply": result.get("suggested_reply"),
    })
    return item
