"""
National Weather Service active alerts = a near-term signal (hurricane/flood
warning right now). No API key required.

Docs: https://www.weather.gov/documentation/services-web-api
"""
import requests

NWS_URL = "https://api.weather.gov/alerts/active/zone/{zone}"
HEADERS = {"User-Agent": "midterm-rental-lead-monitor (contact: you@example.com)"}


def fetch(markets):
    """Return active weather alerts for configured NWS zones."""
    signals = []
    for market in markets:
        zone = market.get("nws_zone")
        if not zone:
            continue
        try:
            resp = requests.get(NWS_URL.format(zone=zone), headers=HEADERS, timeout=20)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"[nws] request failed for {market['name']}: {e}")
            continue

        for feature in resp.json().get("features", []):
            props = feature.get("properties", {})
            severity = props.get("severity", "")
            if severity not in ("Severe", "Extreme"):
                continue  # skip routine/minor advisories, too noisy to act on
            signals.append({
                "source": "NWS",
                "market": market["name"],
                "title": props.get("event", "Weather Alert"),
                "text": (
                    f"{props.get('event')} ({severity}) active for {market['name']}. "
                    f"{props.get('headline', '')} {props.get('description', '')[:400]}"
                ),
                "url": props.get("id", ""),
                "posted_at": props.get("sent"),
                "kind": "market_signal",
            })
    return signals
