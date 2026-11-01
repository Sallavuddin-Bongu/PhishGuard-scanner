"""Rule-based checks. These are SEPARATE evidence from the ML model.

They run on the raw submitted URL (so the "@" check still works after normalization removes user info).
Each check that fires is listed by name with a plain-English reason.
"""
import ipaddress
from urllib.parse import urlsplit

from app.ml.normalize import normalize_url

SUSPICIOUS_WORDS = ["login", "verify", "secure", "account", "update", "signin", "banking", "confirm", "password"]


def _is_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def run_heuristics(raw_url: str, normalized_url: str) -> list[dict]:
    """Return a list of triggered checks, each as {"name": ..., "reason": ...}."""
    triggered = []
    parts = urlsplit(normalized_url)
    host = parts.hostname or ""

    if _is_ip(host):
        triggered.append({"name": "ip_address_host", "reason": "The site address is a raw IP number, not a domain name."})
    if "@" in raw_url:
        triggered.append({"name": "at_symbol", "reason": "The URL contains '@', which can hide the real destination."})
    labels = host.split(".") if host and not _is_ip(host) else []
    if len(labels) - 2 > 3:
        triggered.append({"name": "many_subdomains", "reason": f"The hostname has {len(labels) - 2} subdomain levels."})
    if len(normalized_url) > 75:
        triggered.append({"name": "long_url", "reason": f"The URL is {len(normalized_url)} characters long."})
    if host.count("-") >= 3:
        triggered.append({"name": "many_hyphens", "reason": "The domain uses several hyphens, a common pattern in fake sites."})
    if parts.scheme == "http":
        triggered.append({"name": "not_https", "reason": "The site does not use an encrypted https connection."})
    lowered = normalized_url.lower()
    found_words = [w for w in SUSPICIOUS_WORDS if w in lowered]
    if found_words:
        triggered.append({
            "name": "sensitive_keywords",
            "reason": "The URL contains words often used in login-scam pages: " + ", ".join(found_words) + ".",
        })
    return triggered


HEURISTIC_CHECK_COUNT = 7  # number of checks above; used to turn triggered checks into a 0-100 score
