"""Turns a long risk-explanation sentence into a short, countable label for analytics."""
import re

RULES = [
    (r"raw IP address", "Raw IP address instead of a domain"),
    (r"'@' symbol", "Contains an @ symbol"),
    (r"punycode", "Look-alike (punycode) domain"),
    (r"shortener", "Link shortener hides destination"),
    (r"Does not use HTTPS", "No HTTPS encryption"),
    (r"domain ending", "Risky domain ending (.tk, .xyz ...)"),
    (r"suspicious keyword", "Suspicious keywords (login, verify ...)"),
    (r"subdomain levels", "Too many subdomain levels"),
    (r"several hyphens", "Many hyphens in the domain"),
    (r"URL is long", "Very long URL"),
    (r"non-standard port", "Unusual port number"),
    (r"'//' inside", "Redirect trick ('//' in path)"),
    (r"many digits", "Many digits in the domain"),
    (r"many query", "Many query parameters"),
    (r"brand name", "Brand impersonation"),
    (r"misspelling", "Typosquatting (misspelled brand)"),
    (r"private or reserved", "Points to a private/reserved IP"),
    (r"does not resolve", "Domain does not exist in DNS"),
    (r"No working HTTPS", "No working HTTPS service"),
    (r"certificate was issued only", "Brand-new HTTPS certificate"),
    (r"failed verification", "Invalid HTTPS certificate"),
]
_COMPILED = [(re.compile(p, re.I), label) for p, label in RULES]


def label_for(text: str) -> str:
    for rx, label in _COMPILED:
        if rx.search(text):
            return label
    return re.sub(r"\d+", "N", text)[:60]