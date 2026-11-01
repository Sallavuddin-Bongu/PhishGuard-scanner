"""Rules-based risk scoring with dataset lookup, trusted domains, brand checks and Google Safe Browsing.

Priority order (highest first):
1. Google Safe Browsing flagged the URL -> PHISHING, score at least 90.
2. The exact URL is in the training dataset -> its recorded label.
3. The domain is on TRUSTED_DOMAINS -> SAFE.
4. Clean https URL: https, no rule warnings, Safe Browsing says clear -> SAFE.
5. Otherwise the rules-based score decides the verdict.

Rules-based risk score (0-100):
- Rule part: triggered_checks / total_checks * 100 (a brand-impersonation warning counts as a rule)
- Fact part: notable URL facts / 9 * 100
- risk = min(100, round(1.5 * Rule part + 0.5 * Fact part))

Verdict bands on risk_score:
- PHISHING   : risk_score >= 60
- SUSPICIOUS : 30 <= risk_score < 60
- SAFE       : risk_score < 30

Extra rule: if the verdict would be SAFE but the model's phishing probability is at or above
the decision threshold, the verdict is SUSPICIOUS.

Other safety rules:
- If Google Safe Browsing was unavailable, the explanation says so. An unavailable check is never treated as safe.
- Every SAFE result carries a note that automated detection cannot guarantee a site is safe.
"""
import json
import re
from urllib.parse import urlsplit

from app import dataset_lookup
from app.config import DECISION_THRESHOLD
from app.ml.features import extract_features
from app.ml.heuristics import HEURISTIC_CHECK_COUNT, run_heuristics
from app.ml.normalize import normalize_url
from app.ml.predictor import predict_phishing_probability

RULE_MULTIPLIER = 1.5
FACT_MULTIPLIER = 0.5
FACT_CHECK_COUNT = 9  # number of possible plain-language facts in _feature_facts()
PHISHING_BAND = 60
SUSPICIOUS_BAND = 30
SAFE_NOTE = "Automated URL detection cannot guarantee that a website is safe. Do not enter passwords on unfamiliar sites."

# Well-known sites. A URL on one of these domains (or a subdomain of it) is treated as SAFE
# unless Google Safe Browsing flags it or the dataset records it as phishing.
TRUSTED_DOMAINS = {
    "github.com",
    "google.com",
    "paypal.com",
    "microsoft.com",
    "apple.com",
    "amazon.com",
    "wikipedia.org",
    "youtube.com",
    "bbc.com",
    "reddit.com",
    "nytimes.com",
    "cnn.com",
    "stackoverflow.com",
    "linkedin.com",
    "facebook.com",
    "twitter.com",
    "x.com",
    "imdb.com",
    "nasa.gov",
    "python.org",
    "dropbox.com",
}

# Brand name (as a whole word in the domain) -> its official domain.
# A domain that contains the brand word but is not the official domain gets a warning.
BRAND_DOMAINS = {
    "paypal": "paypal.com",
    "apple": "apple.com",
    "icloud": "icloud.com",
    "amazon": "amazon.com",
    "netflix": "netflix.com",
    "google": "google.com",
    "microsoft": "microsoft.com",
    "outlook": "outlook.com",
    "facebook": "facebook.com",
    "instagram": "instagram.com",
    "whatsapp": "whatsapp.com",
    "dhl": "dhl.com",
    "fedex": "fedex.com",
    "sbi": "sbi.co.in",
    "hdfc": "hdfcbank.com",
    "icici": "icicibank.com",
    "paytm": "paytm.com",
    "binance": "binance.com",
    "coinbase": "coinbase.com",
}


def is_trusted_host(host: str) -> bool:
    return any(host == d or host.endswith("." + d) for d in TRUSTED_DOMAINS)


def _brand_impersonation(host: str) -> tuple[str, str] | None:
    """Return (brand, official_domain) if the host uses a brand name but is not that brand's site."""
    words = set(re.split(r"[.\-]", host.lower()))
    for brand, official in BRAND_DOMAINS.items():
        if brand in words and not (host == official or host.endswith("." + official)):
            return brand, official
    return None


def _feature_facts(f: dict) -> list[str]:
    """Plain-language facts about the URL, only for values that stand out."""
    facts = []
    if f.get("is_ip_host"):
        facts.append("The address is a raw IP number instead of a domain name, which legitimate sites rarely use.")
    if f.get("num_subdomains", 0) >= 3:
        facts.append(f"The domain has {int(f['num_subdomains'])} subdomains, which is unusually many.")
    if f.get("num_hyphens_in_domain", 0) >= 2:
        facts.append(f"The domain name has {int(f['num_hyphens_in_domain'])} hyphens, a common trick in fake sites.")
    if f.get("url_length", 0) >= 75:
        facts.append(f"The full URL is {int(f['url_length'])} characters long, and phishing links are often very long.")
    if f.get("path_depth", 0) >= 4:
        facts.append(f"The path has {int(f['path_depth'])} levels, which is deeper than most normal pages.")
    if f.get("num_percent_encoded", 0) >= 3:
        facts.append("The URL has many percent-encoded characters, which can hide the real destination.")
    if f.get("num_equals", 0) >= 2 or f.get("num_ampersands", 0) >= 3:
        facts.append("The URL carries many query parameters, which phishing pages use to pass along victim data.")
    if f.get("digit_ratio", 0) >= 0.2:
        facts.append(f"About {f['digit_ratio'] * 100:.0f}% of the URL is digits.")
    if f.get("is_https", 1) == 0:
        facts.append("It uses plain HTTP, so anything typed into it is not encrypted.")
    return facts


def _rules_risk(triggered: list[dict], features: dict) -> int:
    rule_part = len(triggered) / HEURISTIC_CHECK_COUNT * 100
    fact_part = len(_feature_facts(features)) / FACT_CHECK_COUNT * 100
    score = RULE_MULTIPLIER * rule_part + FACT_MULTIPLIER * fact_part
    return max(0, min(100, round(score)))


def scan_url(raw_url: str, external: dict | None = None) -> dict:
    external = external or {"status": "not_configured", "threats": []}
    normalized = normalize_url(raw_url)  # may raise InvalidURLError
    parts = urlsplit(normalized)
    host = parts.hostname or ""
    trusted = is_trusted_host(host)
    dataset_label = dataset_lookup.lookup(normalized)  # "phishing", "legitimate", or None

    ml_prob = predict_phishing_probability(normalized)  # may raise ModelNotFoundError / ModelMismatchError
    features = extract_features(normalized)
    triggered = list(run_heuristics(raw_url, normalized))

    brand = _brand_impersonation(host)
    if brand and not trusted:
        name, official = brand
        triggered.append({
            "check": "brand_impersonation",
            "reason": f"The domain uses the brand name '{name}' but is not {official}, a common phishing tactic.",
        })

    heuristic_score = len(triggered) / HEURISTIC_CHECK_COUNT * 100
    risk = _rules_risk(triggered, features)

    # Step 5: verdict from the score bands
    if risk >= PHISHING_BAND:
        verdict = "PHISHING"
    elif risk >= SUSPICIOUS_BAND:
        verdict = "SUSPICIOUS"
    else:
        verdict = "SAFE"
    if verdict == "SAFE" and ml_prob >= DECISION_THRESHOLD:
        verdict = "SUSPICIOUS"

    note = None  # which rule decided the result, used for the explanation

    # Step 3: trusted domain
    if trusted:
        verdict = "SAFE"
        risk = min(risk, 10)
        note = "trusted"

    # Step 4: clean https URL that Safe Browsing did not flag
    clean_https = (
        parts.scheme == "https"
        and len(triggered) == 0
        and external["status"] == "clear"
    )
    if clean_https and note is None:
        verdict = "SAFE"
        risk = min(risk, 15)
        note = "clean_https"

    # Step 2: exact dataset match
    if dataset_label == "phishing":
        verdict = "PHISHING"
        risk = max(risk, 90)
        note = "dataset_phishing"
    elif dataset_label == "legitimate":
        verdict = "SAFE"
        risk = min(risk, 10)
        note = "dataset_legitimate"

    # Step 1: Google Safe Browsing flag always wins
    if external["status"] == "flagged":
        verdict = "PHISHING"
        risk = max(risk, 90)
        note = "flagged"

    explanation = _build_explanation(note, verdict, ml_prob, triggered, external, features, risk)

    return {
        "submitted_url": raw_url,
        "normalized_url": normalized,
        "ml_probability": round(ml_prob, 4),
        "heuristic_score": round(heuristic_score, 1),
        "risk_score": risk,
        "verdict": verdict,
        "external_status": external["status"],
        "external_threats": external.get("threats", []),
        "detection_method": "Dataset lookup + trusted-domain list + brand check + Google Safe Browsing + rule-based checks (model used only as a secondary signal)",
        "triggered_checks": triggered,
        "features": features,
        "explanation": explanation,
        "safety_note": SAFE_NOTE,
    }


def _build_explanation(note, verdict, ml_prob, triggered, external, features, risk) -> str:
    model_line = f"The machine learning model estimates a {ml_prob * 100:.1f}% chance that this URL is phishing."

    if note == "trusted":
        return (
            "This domain is on the trusted list, so the result is SAFE. "
            f"{model_line} That number is not reliable for well-known sites, so it was overridden."
        )
    if note == "clean_https":
        return (
            "This URL uses https, has no rule warnings, and Google Safe Browsing did not flag it, so the result is SAFE. "
            f"{model_line} The model flags many normal pages that have paths, so its score was not used for this decision."
        )
    if note == "dataset_phishing":
        return (
            "This exact URL is in the training dataset, and the dataset records it as PHISHING. "
            f"{model_line}"
        )
    if note == "dataset_legitimate":
        return (
            "This exact URL is in the training dataset, and the dataset records it as LEGITIMATE, so the result is SAFE. "
            f"{model_line}"
        )

    parts = [
        f"The risk score of {risk} is based on the rule checks and the notable details of the URL.",
        model_line,
    ]

    if triggered:
        parts.append(f"Rule checks found {len(triggered)} warning sign(s):")
        parts.extend(f"- {c['reason']}" for c in triggered)
    else:
        parts.append("None of the rule-based checks were triggered.")

    facts = _feature_facts(features)
    if facts:
        parts.append("Notable details about the URL:")
        parts.extend(f"- {fact}" for fact in facts)

    status = external["status"]
    if status == "flagged":
        parts.append("Google Safe Browsing flagged this URL (" + ", ".join(external["threats"]) + ").")
    elif status == "clear":
        parts.append("Google Safe Browsing did not flag this URL.")
    elif status == "unavailable":
        parts.append("The Google Safe Browsing check was unavailable, so it was not used. This does not mean the URL is safe.")

    if verdict == "PHISHING":
        parts.append("Conclusion: this URL is likely a phishing attempt. Do not enter any personal information.")
    elif verdict == "SUSPICIOUS":
        parts.append("Conclusion: this URL shows some warning signs. Verify the site through an official channel before using it.")
    else:
        parts.append("Conclusion: no strong warning signs were found. This does not prove the site is safe.")
    return "\n".join(parts)


def triggered_to_json(triggered: list[dict]) -> str:
    return json.dumps(triggered)


def features_to_json(features: dict) -> str:
    return json.dumps(features)
