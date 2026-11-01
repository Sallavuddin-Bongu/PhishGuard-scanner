import pytest

from app.ml.normalize import InvalidURLError, normalize_url

CASES = [
    ("example.com", "http://example.com"),
    ("EXAMPLE.com", "http://example.com"),
    ("https://www.Example.com/", "https://example.com"),
    ("http://example.com:80/a", "http://example.com/a"),
    ("https://example.com:443/", "https://example.com"),
    ("https://example.com:8443/x", "https://example.com:8443/x"),
    ("https://example.com/path?b=2&a=1#frag", "https://example.com/path?b=2&a=1"),
    ("https://example.com./", "https://example.com"),
    ("  https://example.com/login  ", "https://example.com/login"),
    ("http://user:pass@example.com/", "http://example.com"),
]


@pytest.mark.parametrize("raw,expected", CASES)
def test_normalize_known_inputs(raw, expected):
    assert normalize_url(raw) == expected


def test_missing_scheme_defaults_to_http_same_as_training():
    assert normalize_url("example.com/a").startswith("http://")


@pytest.mark.parametrize("bad", ["", "   ", "ftp://example.com", "https://", "http://exa mple.com", "https://x.com:99999"])
def test_invalid_inputs_are_rejected(bad):
    with pytest.raises(InvalidURLError):
        normalize_url(bad)


def test_idempotent():
    once = normalize_url("HTTPS://WWW.Example.com:443/a/?q=1#x")
    assert normalize_url(once) == once
