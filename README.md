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

# Start local dev server
hugo server --buildDrafts
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

## Project Structure

```
.
├── content/
│   ├── _index.md              # Home page
│   ├── about.md               # About Us page
│   ├── local-news.md          # Local News Stories page
│   └── posts/                 # Blog posts (financial reports, minutes, etc.)
│       ├── 2026-03-07-board-meeting-minutes-march-2026.md
│       ├── 2026-03-01-financial-report-february-2026.md
│       └── ...
├── themes/indianvillage/       # Custom theme
│   ├── layouts/               # HTML templates
│   │   ├── _default/          # Base templates (list, single, baseof)
│   │   └── partials/          # Reusable components (header, sidebar, footer)
│   └── static/css/            # Stylesheet
├── hugo.toml                  # Site configuration
└── .github/workflows/hugo.yml # Auto-deploy on push
```

## Categories

Posts should use one of these categories:
- `HOA` -- Board meeting minutes, association announcements, bylaws
- `Financial` -- Monthly financial reports

## Deployment

Deployment is automatic. Every push to `main` triggers a GitHub Actions workflow that:
1. Builds the site with Hugo
2. Deploys the output to GitHub Pages

No manual deployment steps needed.

## Custom Domain Setup

To point `indianvillagefw.org` at this GitHub Pages site:

1. In GitHub repo settings > Pages, set custom domain to `indianvillagefw.org`
2. At your domain registrar, add DNS records:
   - `A` records pointing to GitHub's IPs: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - `CNAME` record: `www` -> `luapgnibrof.github.io`
3. Enable "Enforce HTTPS" in GitHub Pages settings
