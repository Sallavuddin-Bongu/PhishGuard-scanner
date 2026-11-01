"""The ONE URL normalization used by both training and prediction.

Rules (every caller uses exactly these):
- Missing scheme: "http://" is added. (Training and detection must never disagree on this.)
- Scheme and hostname are lowercased.
- A leading "www." is removed from the hostname.
- A trailing dot on the hostname is removed.
- Default ports are removed (80 for http, 443 for https). Other ports are kept.
- A root path "/" is removed, so "http://a.com/" becomes "http://a.com".
- Fragments (#...) are removed.
- Query strings are kept as they are.
- Only http and https are accepted.
- User info (user:pass@) is removed. The heuristic checks look at the raw input for "@" instead.
"""
from urllib.parse import urlsplit, urlunsplit

DEFAULT_SCHEME = "http"
DEFAULT_PORTS = {"http": 80, "https": 443}
MAX_URL_LENGTH = 2048


class InvalidURLError(ValueError):
    """Raised when a submitted URL cannot be used. The message is safe to show to users."""


def normalize_url(raw: str) -> str:
    if raw is None or not str(raw).strip():
        raise InvalidURLError("Please enter a URL.")
    url = str(raw).strip()
    if len(url) > MAX_URL_LENGTH:
        raise InvalidURLError(f"URL is too long (maximum {MAX_URL_LENGTH} characters).")
    if " " in url or any(ord(c) < 32 for c in url):
        raise InvalidURLError("URL contains spaces or control characters.")
    if "://" not in url:
        url = f"{DEFAULT_SCHEME}://{url}"

    try:
        parts = urlsplit(url)
        port = parts.port  # raises ValueError for invalid ports
    except ValueError:
        raise InvalidURLError("URL is malformed.")

    scheme = parts.scheme.lower()
    if scheme not in DEFAULT_PORTS:
        raise InvalidURLError("Only http:// and https:// URLs can be scanned.")

    host = (parts.hostname or "").lower().rstrip(".")
    if not host:
        raise InvalidURLError("URL has no hostname.")
    if host.startswith("www."):
        host = host[4:]
    if not host:
        raise InvalidURLError("URL has no hostname.")

    netloc = host
    if port is not None and port != DEFAULT_PORTS[scheme]:
        netloc = f"{host}:{port}"

    path = parts.path
    if path == "/":
        path = ""

    return urlunsplit((scheme, netloc, path, parts.query, ""))
