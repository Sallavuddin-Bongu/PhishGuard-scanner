"""URL-only features. Training and prediction both call extract_features() from this file.

These features use only the URL text. They do NOT use page HTML, JavaScript, or
page metadata, because a URL string alone cannot provide those.

Note: "/", ":" and "." are structural characters of every URL (https://, paths, domains),
so they are NOT counted as special characters. Counting them made every page with a path
look suspicious.
"""
import ipaddress
from urllib.parse import urlsplit

FEATURE_NAMES = [
    "url_length",
    "domain_length",
    "is_ip_host",
    "tld_length",
    "num_subdomains",
    "num_letters",
    "letter_ratio",
    "num_digits",
    "digit_ratio",
    "num_special",
    "special_ratio",
    "num_equals",
    "num_question_marks",
    "num_ampersands",
    "num_percent_encoded",
    "percent_encoded_ratio",
    "num_hyphens_in_domain",
    "num_dots",
    "path_depth",
    "is_https",
]

STRUCTURAL_CHARS = set("/:.")


def _is_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def extract_features(normalized_url: str) -> dict:
    """Return the feature dict. Input must already be normalized by normalize_url()."""
    parts = urlsplit(normalized_url)
    host = parts.hostname or ""
    url = normalized_url
    length = max(len(url), 1)

    is_ip = _is_ip(host)
    labels = [] if is_ip or not host else host.split(".")
    tld_length = len(labels[-1]) if len(labels) >= 2 else 0
    num_subdomains = max(len(labels) - 2, 0)

    num_letters = sum(c.isalpha() for c in url)
    num_digits = sum(c.isdigit() for c in url)
    num_special = sum(not c.isalnum() and c not in STRUCTURAL_CHARS for c in url)
    num_percent = url.count("%")
    path_segments = [s for s in parts.path.split("/") if s]

    return {
        "url_length": len(url),
        "domain_length": len(host),
        "is_ip_host": int(is_ip),
        "tld_length": tld_length,
        "num_subdomains": num_subdomains,
        "num_letters": num_letters,
        "letter_ratio": num_letters / length,
        "num_digits": num_digits,
        "digit_ratio": num_digits / length,
        "num_special": num_special,
        "special_ratio": num_special / length,
        "num_equals": url.count("="),
        "num_question_marks": url.count("?"),
        "num_ampersands": url.count("&"),
        "num_percent_encoded": num_percent,
        "percent_encoded_ratio": num_percent / length,
        "num_hyphens_in_domain": host.count("-"),
        "num_dots": url.count("."),
        "path_depth": len(path_segments),
        "is_https": int(parts.scheme == "https"),
    }