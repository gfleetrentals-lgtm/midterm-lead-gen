"""
FEMA disaster declarations = a demand SIGNAL, not an individual lead.
When a county gets declared a disaster area, that's your early warning that
insurance-claim tenants and construction/restoration crews are about to need
housing there. No API key required; this is fully public data.

Docs: https://www.fema.gov/about/openfema/api
"""
import datetime
import requests

FEMA_URL = "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries"


def fetch(markets, lookback_days=30):
    """Return a list of recent disaster declarations relevant to configured markets."""
    since = (datetime.datetime.utcnow() - datetime.timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    signals = []

    for market in markets:
        # Filter by state AND county server-side (via startswith on
        # designatedArea) — the API returns declarations most-recent-first,
        # and a client-side county filter after a capped $top would silently
        # miss county hits buried past that cap during a busy season.
        params = {
            "$filter": (
                f"state eq '{market['state']}' and "
                f"declarationDate ge '{since}' and "
                f"startswith(designatedArea,'{market['county_name']}')"
            ),
            "$orderby": "declarationDate desc",
            "$top": 50,
        }
        try:
            resp = requests.get(FEMA_URL, params=params, timeout=20)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"[fema] request failed for {market['name']}: {e}")
            continue

        for row in resp.json().get("DisasterDeclarationsSummaries", []):
            signals.append({
                "source": "FEMA",
                "market": market["name"],
                "title": f"{row.get('incidentType', 'Disaster')} declared — {row.get('designatedArea')}",
                "text": (
                    f"Disaster declaration in {row.get('designatedArea')}, {market['state']}. "
                    f"Type: {row.get('incidentType')}. "
                    f"Declared: {row.get('declarationDate')}. "
                    f"Programs: IA={row.get('ihProgramDeclared')}, PA={row.get('paProgramDeclared')}. "
                    "Expect a wave of insurance-claim tenants and construction/restoration "
                    "crews needing housing in this area over the following weeks-to-months."
                ),
                "url": "https://www.fema.gov/disaster/" + str(row.get("disasterNumber", "")),
                "posted_at": row.get("declarationDate"),
                "kind": "market_signal",
            })
    return signals
