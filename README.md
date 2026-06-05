# Indian Village Community Association Website

**[indianvillagefw.org](https://indianvillagefw.org)**

A static website for the Historic Indian Village neighborhood in Waynedale, Fort Wayne, Indiana. Built with [Hugo](https://gohugo.io/) and hosted on GitHub Pages.

## Quick Start

### Prerequisites

- [Hugo Extended](https://gohugo.io/installation/) (v0.159+)
- [Git](https://git-scm.com/)

### Local Development

```bash
# Clone the repo
git clone git@github.com:luapgnibrof/indianvillagefw.org.git
cd indianvillagefw.org

# Start local dev server (includes future-dated posts)
hugo server --buildDrafts --buildFuture
```

Open http://localhost:1313 in your browser. Changes auto-reload.

## How to Add a New Post

1. Create a new Markdown file in `content/posts/`:

```bash
hugo new posts/2026-04-01-my-new-post.md
```

2. Edit the file with your content:

```markdown
---
title: "My New Post Title"
date: 2026-04-01T00:00:00-04:00
author: "Your Name"
categories: ["HOA"]
---

Your post content goes here. Use standard Markdown formatting.
```

3. Commit and push:

```bash
git add .
git commit -m "Add April 2026 post"
git push
```

The site will automatically rebuild and deploy within ~1 minute.

## How to Edit a Page

- **About Us**: Edit `content/about.md`
- **Local News Stories**: Edit `content/local-news.md`
- **Navigation menus**: Edit `hugo.toml` under `[menu]`
- **Sidebar resources**: Edit `themes/indianvillage/layouts/partials/sidebar.html`

## Categories

Posts should use one of these categories:

| Category | Use for |
|----------|---------|
| `HOA` | Board meeting minutes, bylaws, association announcements |
| `Financial` | Monthly financial reports |
| `Newsletter` | Monthly newsletters |
| `Event` | Community events, garage sales, parades, concerts |
| `Local News` | News stories about Indian Village from local media |

### Event Posts & the Homepage Callout

Posts with `categories: ["Event"]` and a **future date** are treated specially: the nearest upcoming event is automatically shown in a highlighted callout box at the top of the homepage. Once the event date passes, the callout advances to the next upcoming event automatically. No manual homepage edits are needed.

## Local Projects (`data/projects.yaml`)

The **Local Projects** page is driven by `data/projects.yaml`. Each project entry controls the status badge, latest update text, timeline, key dates, and links shown on that page — and project updates also appear in the homepage feed.

### Updating a project manually

Edit `data/projects.yaml` directly. Key fields:

| Field | Description |
|-------|-------------|
| `status` | Controls badge color: `active` (green), `planned` (blue), `completed` (grey) |
| `status_label` | Text shown in the badge, e.g. `"Under Construction"`, `"In Progress"`, `"Complete"` |
| `latest_update` | One-line summary shown in the homepage feed |
| `updated` | Date of last update in `YYYY-MM-DD` format |
| `neighborhood_impact` | Longer description shown on the projects detail page |

### Automated project updates

Projects that have an `engage_url` pointing to an Engage Fort Wayne project page are checked weekly by the `check-projects` workflow (see [Automations](#automations)). When the script detects changed text on the page, it opens a pull request with the updated `latest_update` field for review before merging.

Projects without an `engage_url` (e.g. NIPSCO) must be updated manually.

## Automations

Three GitHub Actions workflows run automatically:

### 1. Deploy (`hugo.yml`)
Triggered on every push to `main`. Fetches the latest Waynedale News RSS feed into `data/waynedale_feed.json` (falls back gracefully if the feed is unreachable), builds the Hugo site, and deploys to GitHub Pages. The build uses `--buildFuture` so future-dated posts (e.g. upcoming events) are always included.

### 2. Local News Fetcher (`fetch-news.yml`)
Runs every **Monday at 8 AM Eastern**. Searches Google News and the Waynedale News RSS feed for articles mentioning "Indian Village". New articles are saved as draft posts in `content/posts/` and a pull request is opened for review. Merge the PR to publish; close it to discard.

Seen articles are tracked in `.github/seen-articles.json` to avoid duplicates across runs.

### 3. Project Updates (`check-projects.yml`)
Runs every **Wednesday at 9 AM Eastern**. Scrapes each project's Engage Fort Wayne page and compares the extracted text against the `latest_update` field in `data/projects.yaml`. If anything changed, it updates the file and opens a pull request. The PR description summarizes what changed on each project page.

### Required repo settings

For the PR-creating workflows to work, the repository needs:

- **Settings → Actions → General → Workflow permissions**: set to *Read and write permissions*
- **Allow GitHub Actions to create and approve pull requests**: checked

These are already configured. If workflows start failing with "not permitted to create pull requests", re-check these settings.

## Project Structure

```
.
├── content/
│   ├── _index.md              # Home page welcome text
│   ├── about.md               # About Us page
│   ├── events.md              # Events page
│   ├── local-news.md          # Local News Stories page
│   ├── local-projects.md      # Local Projects page
│   └── posts/                 # All posts (news, minutes, financials, events)
├── data/
│   ├── projects.yaml          # Local projects data (manually maintained + auto-updated)
│   └── waynedale_feed.json    # Waynedale News sidebar feed (auto-generated at build time)
├── themes/indianvillage/
│   ├── layouts/
│   │   ├── index.html         # Homepage template (event callout + post feed)
│   │   ├── _default/          # Base templates (list, single, baseof)
│   │   ├── page/              # Per-page templates (events, projects, news, etc.)
│   │   └── partials/          # Reusable components (header, sidebar, footer)
│   └── static/css/style.css   # Stylesheet
├── .github/
│   ├── scripts/
│   │   ├── fetch-news.py      # Local news fetcher script
│   │   └── check-projects.py  # Engage Fort Wayne project scraper
│   ├── workflows/
│   │   ├── hugo.yml           # Deploy on push
│   │   ├── fetch-news.yml     # Weekly news automation
│   │   └── check-projects.yml # Weekly project update automation
│   ├── seen-articles.json     # Tracks already-processed news articles
│   └── pr-body*.md            # Auto-generated PR descriptions (gitignored)
└── hugo.toml                  # Site configuration
```

## Deployment

Deployment is automatic. Every push to `main` triggers the `hugo.yml` workflow which builds and deploys to GitHub Pages within ~1 minute.

Build status: https://github.com/luapgnibrof/indianvillagefw.org/actions

## Custom Domain Setup

To point `indianvillagefw.org` at this GitHub Pages site:

1. In GitHub repo settings > Pages, set custom domain to `indianvillagefw.org`
2. At your domain registrar, add DNS records:
   - `A` records pointing to GitHub's IPs: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - `CNAME` record: `www` -> `luapgnibrof.github.io`
3. Enable "Enforce HTTPS" in GitHub Pages settings
