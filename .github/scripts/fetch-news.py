# /// script
# requires-python = ">=3.10"
# dependencies = ["requests", "googlenewsdecoder"]
# ///
"""
Fetch news articles mentioning Indian Village Fort Wayne from RSS feeds,
filter for relevance, and create Hugo draft posts for new articles.

Runs as a GitHub Actions workflow (weekly) or manually via `uv run`.
"""

import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.parse import urlparse

import requests
from googlenewsdecoder import new_decoderv1

SITE_ROOT = Path(__file__).resolve().parent.parent.parent
POSTS_DIR = SITE_ROOT / "content" / "posts"
SEEN_FILE = SITE_ROOT / ".github" / "seen-articles.json"

FEEDS = {
    "Google News": (
        "https://news.google.com/rss/search?"
        "q=%22Indian+Village%22+%22Fort+Wayne%22&hl=en-US&gl=US&ceid=US:en"
    ),
    "Waynedale News": "https://waynedalenews.com/feed/",
}

# Keywords that must appear in the title or description (case-insensitive)
REQUIRE_ANY = ["indian village"]

# Reject articles whose titles match these patterns (not about the neighborhood)
REJECT_PATTERNS = [
    re.compile(r"\bobituar", re.I),
    re.compile(r"\bdetroit\b", re.I),
    re.compile(r"\bpickawillany\b", re.I),
    re.compile(r"\bbattle of the wabash\b", re.I),
]


def load_seen() -> dict:
    if SEEN_FILE.exists():
        return json.loads(SEEN_FILE.read_text(encoding="utf-8"))
    return {}


def save_seen(seen: dict):
    SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    SEEN_FILE.write_text(json.dumps(seen, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def url_key(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def normalize_url(url: str) -> str:
    """Normalize URL for deduplication: strip scheme, trailing slash, query params."""
    parsed = urlparse(url)
    path = parsed.path.rstrip("/").lower()
    host = parsed.netloc.lower().removeprefix("www.")
    return f"{host}{path}"


def strip_html(text: str) -> str:
    text = unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def is_relevant(title: str, description: str) -> bool:
    combined = f"{title} {description}".lower()
    if not any(kw in combined for kw in REQUIRE_ANY):
        return False
    if any(pat.search(title) for pat in REJECT_PATTERNS):
        return False
    return True


def parse_rss_date(date_str: str) -> datetime:
    """Parse RFC 822 date from RSS feeds."""
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S GMT",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return datetime.now(tz=timezone.utc)


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:80]


def normalize_quotes(text: str) -> str:
    """Replace smart/curly quotes with straight ASCII quotes."""
    text = text.replace("\u2018", "'").replace("\u2019", "'")  # single quotes
    text = text.replace("\u201c", '"').replace("\u201d", '"')  # double quotes
    text = text.replace("\u2013", "-").replace("\u2014", "-")  # dashes
    return text


def clean_title(title: str) -> str:
    """Remove the ' - Source' suffix that Google News appends and normalize quotes."""
    title = normalize_quotes(title)
    if " - " in title:
        return title.rsplit(" - ", 1)[0].strip()
    return title.strip()


def extract_source_from_title(title: str, feed_name: str) -> str:
    """Extract source name from Google News title format 'Headline - Source'."""
    if " - " in title and feed_name == "Google News":
        return title.rsplit(" - ", 1)[1].strip()
    return feed_name


def resolve_google_news_url(url: str) -> str | None:
    """Decode a Google News redirect URL to the original article URL."""
    try:
        result = new_decoderv1(url)
        if result.get("status"):
            return result["decoded_url"]
    except Exception:
        pass
    return None


def fetch_feed_items(url: str) -> list[dict]:
    """Fetch and parse an RSS feed, returning a list of item dicts."""
    resp = requests.get(url, timeout=30, headers={"User-Agent": "IndianVillageNewsBot/1.0"})
    resp.raise_for_status()
    root = ET.fromstring(resp.text)

    items = []
    for item_el in root.findall(".//item"):
        title = item_el.findtext("title", "").strip()
        link = item_el.findtext("link", "").strip()
        desc_raw = item_el.findtext("description", "") or ""
        pub_date = item_el.findtext("pubDate", "")

        # Some feeds use content:encoded for full text
        content_ns = "{http://purl.org/rss/1.0/modules/content/}"
        content = item_el.findtext(f"{content_ns}encoded", "")

        items.append({
            "title": title,
            "link": link,
            "description": strip_html(desc_raw),
            "content": strip_html(content) if content else "",
            "pubDate": pub_date,
        })
    return items


def create_post(title: str, date: datetime, source: str, url: str, summary: str) -> Path:
    date_str = date.strftime("%Y-%m-%d")
    slug = slugify(title)
    filename = f"{date_str}-{slug}.md"
    filepath = POSTS_DIR / filename

    tz_offset = date.strftime("%z") or "+0000"
    frontmatter_date = date.strftime(f"%Y-%m-%dT%H:%M:%S{tz_offset}")

    content = f"""---
title: "{title.replace('"', '\\"')}"
date: {frontmatter_date}
author: "{source.replace('"', '\\"')}"
categories: ["Local News"]
externalUrl: "{url}"
---

{summary}

*Source: [{source}]({url})*
"""
    filepath.write_text(content, encoding="utf-8")
    return filepath


def main():
    seen = load_seen()
    new_articles = []

    # Collect normalized URLs from all existing posts for deduplication
    existing_urls = set()
    for post in POSTS_DIR.glob("*.md"):
        text = post.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(r'https?://[^\s)"]+', text):
            raw = match.group().rstrip(".")
            existing_urls.add(normalize_url(raw))

    for feed_name, feed_url in FEEDS.items():
        print(f"Fetching {feed_name}...")
        try:
            items = fetch_feed_items(feed_url)
        except Exception as e:
            print(f"  Error fetching {feed_name}: {e}")
            continue

        print(f"  Found {len(items)} items")

        for item in items:
            title = item["title"]
            description = item["description"]
            link = item["link"]

            if not is_relevant(title, description):
                continue

            # Resolve Google News redirect URLs to original article URLs
            article_url = link
            if "news.google.com" in link:
                resolved = resolve_google_news_url(link)
                if resolved:
                    article_url = resolved
                    print(f"  Resolved: {resolved[:80]}")
                else:
                    print(f"  Warning: Could not resolve Google News URL for: {title[:60]}")

            # Deduplicate by both the original link and the resolved URL
            for check_url in {link, article_url}:
                key = url_key(check_url)
                if key in seen:
                    break
            else:
                key = url_key(article_url)

            if key in seen:
                continue

            # Check if this article's URL already exists in any post
            norm = normalize_url(article_url)
            if norm in existing_urls:
                seen[key] = {"title": title, "url": article_url, "skipped": "already exists"}
                continue

            source = extract_source_from_title(title, feed_name)
            cleaned_title = clean_title(title)
            date = parse_rss_date(item["pubDate"])

            # Use description as summary, truncate if needed
            summary = normalize_quotes(description[:500] + "..." if len(description) > 500 else description)
            if not summary or len(summary) < 20:
                summary = f"A new article about Indian Village has been published by {source}."

            filepath = create_post(cleaned_title, date, source, article_url, summary)
            new_articles.append({"title": cleaned_title, "source": source, "file": str(filepath.name)})
            seen[key] = {"title": cleaned_title, "url": article_url, "added": datetime.now(tz=timezone.utc).isoformat()}
            print(f"  + {cleaned_title} ({source})")

    save_seen(seen)

    if new_articles:
        print(f"\nFound {len(new_articles)} new article(s).")
        # Write summary for the PR body
        summary_path = SITE_ROOT / ".github" / "pr-body.md"
        lines = ["## New Local News Articles Found\n"]
        for a in new_articles:
            lines.append(f"- **{a['title']}** ({a['source']}) -> `{a['file']}`")
        lines.append("\n\nPlease review these draft posts. Edit or delete any that aren't relevant before merging.")
        summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    else:
        print("\nNo new articles found.")

    # Exit code tells the workflow whether to create a PR
    sys.exit(0 if new_articles else 1)


if __name__ == "__main__":
    main()
