"""Bounded public-source discovery. Results are untrusted research leads."""
import datetime
import html
from html.parser import HTMLParser
import json
import re
import urllib.parse
import urllib.request

ENDPOINT = "https://en.wikipedia.org/w/api.php"
MAX_BYTES = 256_000
REFERENCE_HOSTS = {"www.desmos.com", "www.calculator.net"}


class PageText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hidden = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.hidden += 1
        if not self.hidden and tag in ("input", "button"):
            values = dict(attrs)
            for key in ("aria-label", "value", "title"):
                if values.get(key):
                    self.parts.append(values[key])

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.hidden:
            self.hidden -= 1

    def handle_data(self, data):
        if not self.hidden and data.strip():
            self.parts.append(data.strip())


def inspect_references(urls):
    if len(urls) > 3:
        raise ValueError("At most three reference URLs are allowed")
    result = []
    opener = urllib.request.build_opener(NoRedirect())
    for url in urls:
        parsed = urllib.parse.urlsplit(url)
        if (parsed.scheme != "https" or parsed.hostname not in REFERENCE_HOSTS
                or parsed.username or parsed.password or parsed.port not in (None, 443)):
            raise ValueError("Reference URL is not on the approved public host list")
        request = urllib.request.Request(url, headers={"User-Agent": "SoftwareFactoryResearch/0.1"})
        with opener.open(request, timeout=15) as response:
            body = response.read(MAX_BYTES + 1)
        if len(body) > MAX_BYTES:
            raise ValueError("Reference response exceeds size limit")
        parser = PageText()
        parser.feed(body.decode("utf-8", errors="replace"))
        result.append({"url": url, "accessed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                       "text": " ".join(parser.parts)[:12000],
                       "limitation": "Static HTML only; no browser interaction or market-share verification."})
    return result


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Research redirects are not allowed")


def discover(query):
    if not isinstance(query, str) or not query.strip() or len(query) > 200:
        raise ValueError("Research query must contain 1 to 200 characters")
    params = urllib.parse.urlencode({"action": "query", "list": "search", "srsearch": query,
                                    "format": "json", "srlimit": 5})
    request = urllib.request.Request(ENDPOINT + "?" + params,
        headers={"User-Agent": "SoftwareFactoryResearch/0.1 (https://github.com/chintanpuggalok/software-factory)"})
    opener = urllib.request.build_opener(NoRedirect())
    with opener.open(request, timeout=15) as response:
        body = response.read(MAX_BYTES + 1)
    if len(body) > MAX_BYTES:
        raise ValueError("Research response exceeds size limit")
    data = json.loads(body)
    hits = data.get("query", {}).get("search", [])
    if not isinstance(hits, list):
        raise ValueError("Invalid research response")
    results = []
    for hit in hits[:5]:
        if not isinstance(hit, dict) or not isinstance(hit.get("title"), str):
            continue
        title = hit["title"][:300]
        snippet = html.unescape(re.sub(r"<[^>]*>", "", str(hit.get("snippet", ""))))[:800]
        results.append({"title": title,
                        "url": "https://en.wikipedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_")),
                        "snippet": snippet,
                        "last_edited": hit.get("timestamp")})
    return {"query": query, "accessed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "source": ENDPOINT, "results": results,
            "limitation": "Search snippets are untrusted leads, not verified market-share evidence."}
