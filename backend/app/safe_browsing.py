"""Google Safe Browsing lookup. This is EXTERNAL threat intelligence, kept separate from the ML model.

Status values:
- "not_configured": no API key in .env (the app still works)
- "clear":          Google returned no matches
- "flagged":        Google returned at least one match (threat types listed)
- "unavailable":    the request failed, timed out, or was rate-limited. This is NOT proof the URL is safe.
"""
import httpx

from app import config

ENDPOINT = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
THREAT_TYPES = ["SOCIAL_ENGINEERING", "MALWARE", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"]


def check_url(url: str) -> dict:
    key = config.GOOGLE_SAFE_BROWSING_API_KEY
    if not key:
        return {"status": "not_configured", "threats": []}

    body = {
        "client": {"clientId": "phishguard", "clientVersion": "1.0.0"},
        "threatInfo": {
            "threatTypes": THREAT_TYPES,
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}],
        },
    }
    try:
        response = httpx.post(ENDPOINT, params={"key": key}, json=body, timeout=5.0)
    except httpx.HTTPError:
        return {"status": "unavailable", "threats": [], "message": "Google Safe Browsing did not respond in time."}

    if response.status_code == 429:
        return {"status": "unavailable", "threats": [], "message": "Google Safe Browsing rate limit reached."}
    if response.status_code != 200:
        return {"status": "unavailable", "threats": [], "message": "Google Safe Browsing returned an error."}

    try:
        matches = response.json().get("matches", [])
    except ValueError:
        return {"status": "unavailable", "threats": [], "message": "Google Safe Browsing sent an unreadable reply."}

    if matches:
        threats = sorted({m.get("threatType", "UNKNOWN") for m in matches})
        return {"status": "flagged", "threats": threats}
    return {"status": "clear", "threats": []}
