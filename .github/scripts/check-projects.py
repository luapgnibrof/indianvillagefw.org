# /// script
# requires-python = ">=3.10"
# dependencies = ["requests", "beautifulsoup4", "pyyaml"]
# ///
"""
Check Engage Fort Wayne project pages for construction updates.
Compares latest updates with what's in data/projects.yaml and
updates the file if anything has changed.

Runs as a GitHub Actions workflow (weekly) or manually via `uv run`.
"""

import re
import sys
from datetime import date
from pathlib import Path

import requests
import yaml
from bs4 import BeautifulSoup

SITE_ROOT = Path(__file__).resolve().parent.parent.parent
PROJECTS_FILE = SITE_ROOT / "data" / "projects.yaml"
PR_BODY_FILE = SITE_ROOT / ".github" / "pr-body-projects.md"

HEADERS = {"User-Agent": "IndianVillageProjectBot/1.0"}
TIMEOUT = 30


def fetch_page(url: str) -> str:
    """Fetch a page and return its HTML content."""
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.text


def extract_construction_update(html: str) -> str | None:
    """Extract the latest construction update text from an Engage Fort Wayne page."""
    soup = BeautifulSoup(html, "html.parser")

    # Strategy 1: Look for "Construction update" heading and grab content after it
    for heading in soup.find_all(["h2", "h3", "h4"]):
        if "construction update" in heading.get_text(strip=True).lower():
            # Collect text from following siblings until next major heading
            parts = []
            for sib in heading.find_next_siblings():
                if sib.name in ("h1", "h2") and "previous" not in sib.get_text(strip=True).lower():
                    break
                # Stop at "Previous Construction Updates" section
                text = sib.get_text(strip=True)
                if "previous construction updates" in text.lower():
                    break
                if text:
                    parts.append(text)
            if parts:
                return " ".join(parts)

    # Strategy 2: Look for bold date pattern (e.g., "March 19, 2026:") in page content
    text = soup.get_text()
    date_pattern = re.compile(
        r"((?:January|February|March|April|May|June|July|August|September|October|November|December)"
        r"\s+\d{1,2},?\s+\d{4})\s*[:\u2014\u2013-]\s*(.+?)(?=\n\n|\Z)",
        re.DOTALL,
    )
    match = date_pattern.search(text)
    if match:
        date_str = match.group(1).strip()
        body = re.sub(r"\s+", " ", match.group(2)).strip()
        if body:
            return f"{date_str} — {body[:500]}"

    # Strategy 3: Look for timeline items marked as "active"
    # The Engage pages use "Timeline item N - active" patterns
    active_items = []
    for el in soup.find_all(string=re.compile(r"Timeline item.*active", re.I)):
        parent = el.parent
        if parent:
            # Get the next few siblings for the timeline content
            parts = []
            for sib in parent.find_next_siblings():
                text = sib.get_text(strip=True)
                if not text or "timeline item" in text.lower():
                    break
                parts.append(text)
            if parts:
                active_items.append(" ".join(parts))
    if active_items:
        return " | ".join(active_items)

    return None


def extract_key_dates_update(html: str) -> str | None:
    """Extract key dates content as a fallback for pages without construction updates."""
    soup = BeautifulSoup(html, "html.parser")

    for heading in soup.find_all(["h2", "h3", "h4"]):
        if "key date" in heading.get_text(strip=True).lower():
            parts = []
            for sib in heading.find_next_siblings():
                if sib.name in ("h1", "h2", "h3"):
                    break
                text = sib.get_text(strip=True)
                if text:
                    parts.append(text)
            if parts:
                return " ".join(parts)[:500]

    return None


def normalize_text(text: str) -> str:
    """Normalize whitespace and smart quotes for comparison."""
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def main():
    if not PROJECTS_FILE.exists():
        print(f"Error: {PROJECTS_FILE} not found")
        sys.exit(1)

    data = yaml.safe_load(PROJECTS_FILE.read_text(encoding="utf-8"))
    projects = data.get("projects", [])
    changes = []

    for project in projects:
        name = project.get("name", "Unknown")
        engage_url = project.get("engage_url")
        if not engage_url:
            print(f"  Skipping {name} (no engage_url)")
            continue

        print(f"Checking {name}...")
        try:
            html = fetch_page(engage_url)
        except Exception as e:
            print(f"  Error fetching {engage_url}: {e}")
            continue

        # Try construction update first, then key dates
        new_update = extract_construction_update(html)
        if not new_update:
            new_update = extract_key_dates_update(html)
        if not new_update:
            print(f"  No update text found on page")
            continue

        new_update = normalize_text(new_update)
        old_update = normalize_text(project.get("latest_update", ""))

        if new_update != old_update:
            print(f"  UPDATE FOUND: {new_update[:120]}...")
            project["latest_update"] = new_update
            project["updated"] = date.today().isoformat()
            changes.append({
                "name": name,
                "old": old_update[:100] + "..." if len(old_update) > 100 else old_update,
                "new": new_update[:200] + "..." if len(new_update) > 200 else new_update,
            })
        else:
            print(f"  No changes")

    if changes:
        # Write updated YAML
        # Use a custom representer to handle long strings nicely
        class Dumper(yaml.SafeDumper):
            pass

        def str_representer(dumper, data):
            if "\n" in data or len(data) > 100:
                return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')
            return dumper.represent_scalar("tag:yaml.org,2002:str", data)

        Dumper.add_representer(str, str_representer)

        PROJECTS_FILE.write_text(
            yaml.dump(data, Dumper=Dumper, default_flow_style=False, allow_unicode=True, sort_keys=False, width=200),
            encoding="utf-8",
        )

        # Write PR body
        lines = ["## Local Project Updates Found\n"]
        for c in changes:
            lines.append(f"### {c['name']}")
            lines.append(f"**New:** {c['new']}")
            lines.append("")
        lines.append(
            "\nPlease review these updates before merging. "
            "The script extracted text from Engage Fort Wayne project pages."
        )
        PR_BODY_FILE.parent.mkdir(parents=True, exist_ok=True)
        PR_BODY_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

        print(f"\nFound {len(changes)} update(s).")
    else:
        print("\nNo updates found.")

    # Exit code tells the workflow whether to create a PR
    sys.exit(0 if changes else 1)


if __name__ == "__main__":
    main()
