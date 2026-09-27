import os
import sys

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)


def session(headers=None, total=4, backoff=2.0):
    s = requests.Session()
    retry = Retry(
        total=total,
        backoff_factor=backoff,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET", "POST"),
        respect_retry_after_header=True,
        raise_on_status=False,
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.mount("http://", HTTPAdapter(max_retries=retry))
    s.headers.update({"User-Agent": UA, **(headers or {})})
    return s


def check(r):
    """raise_for_status that shows the API's error body but never the query string (it may hold API keys)."""
    if r.status_code >= 400:
        raise requests.HTTPError(f"HTTP {r.status_code} {r.url.split('?')[0]}: {r.text[:500]}", response=r)
    return r


def require_env(name):
    """Return the env var, or emit a GitHub Actions warning and exit 0 so other collectors still run."""
    value = os.environ.get(name, "").strip()
    if not value:
        print(f"::warning::{name} is not set - skipping this collector")
        sys.exit(0)
    return value


def env_int(name, default):
    raw = os.environ.get(name, "").strip()
    return int(raw) if raw else default
