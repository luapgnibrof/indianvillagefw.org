# How to Add & Edit Posts on the Indian Village Website

This guide is for IVCA Board members who need to publish content to [indianvillagefw.org](https://indianvillagefw.org). No coding experience is required.

---

## How the Site Works (30-second version)

The website is a collection of simple text files stored on GitHub. When you add or edit a file and save it, the site automatically rebuilds and publishes itself -- usually within about 1 minute. That's it.

Posts are written in **Markdown**, a lightweight way to format text. If you've ever used Reddit, Slack, or Discord formatting, you've already used Markdown.

---

## Option A: Edit Directly on GitHub (Easiest -- No Software Needed)

This is the simplest method. All you need is a web browser and a GitHub account.

### First-Time Setup

1. Create a free GitHub account at https://github.com/signup
2. Ask Paul to add you as a collaborator on the repository

### Adding a New Post

1. Go to https://github.com/luapgnibrof/indianvillagefw.org
2. Navigate to the **content/posts/** folder
3. Click the **"Add file"** button (top right), then **"Create new file"**
4. Name your file using this pattern:

   ```
   YYYY-MM-DD-short-description.md
   ```

   Examples:
   - `2026-04-01-financial-report-march-2026.md`
   - `2026-04-15-board-meeting-minutes-april-2026.md`
   - `2026-05-01-neighborhood-cleanup-day.md`

5. Paste the following template into the file and fill in your content:

   ```
   ---
   title: "Your Post Title Here"
   date: 2026-04-01T00:00:00-04:00
   author: "Your Name"
   categories: ["Financial"]
   ---

   Write your post content here.
   ```

6. Click **"Commit changes..."** (green button)
7. In the popup, leave "Commit directly to the main branch" selected
8. Click **"Commit changes"**

The site will rebuild and your post will be live within about 1 minute.

### Editing an Existing Post

1. Go to https://github.com/luapgnibrof/indianvillagefw.org
2. Navigate to **content/posts/** and click the file you want to edit
3. Click the **pencil icon** (top right of the file content) to edit
4. Make your changes
5. Click **"Commit changes..."** and confirm

---

## Option B: Edit on Your Computer (For Frequent Contributors)

If you'll be posting regularly, working locally lets you preview changes before publishing.

### One-Time Setup

1. Install [Git](https://git-scm.com/downloads)
2. Install [Hugo Extended](https://gohugo.io/installation/) (v0.159 or newer)
3. Clone the repository:

   ```
   git clone https://github.com/luapgnibrof/indianvillagefw.org.git
   cd indianvillagefw.org
   ```

### Adding a New Post

1. Create a new file in the `content/posts/` folder. You can copy an existing post as a starting point, or run:

   ```
   hugo new posts/2026-04-01-financial-report-march-2026.md
   ```

2. Open the file in any text editor (Notepad, VS Code, etc.) and write your content

3. Preview locally:

   ```
   hugo server
   ```

   Open http://localhost:1313 in your browser. Changes auto-reload as you save.

4. When you're happy with it, publish:

   ```
   git add .
   git commit -m "Add March 2026 financial report"
   git push
   ```

The site will be live within about 1 minute.

---

## Post Template Reference

Every post starts with a **front matter** block between the `---` lines. This tells the site how to display the post.

```
---
title: "Financial Report - March 2026"
date: 2026-04-01T00:00:00-04:00
author: "Monica Hadsall"
categories: ["Financial"]
---
```

| Field        | What to put                                                              |
|-------------|--------------------------------------------------------------------------|
| `title`     | The post title, in quotes                                                |
| `date`      | Publication date in `YYYY-MM-DDT00:00:00-04:00` format (Eastern time)    |
| `author`    | Your name, in quotes                                                     |
| `categories`| One of: `["Newsletter"]`, `["Financial"]`, `["HOA"]`, `["Event"]`, or `["Local News"]` |

### Categories

| Category      | Use for                                                  |
|--------------|----------------------------------------------------------|
| `Newsletter` | Monthly newsletters (link to Mailchimp archive)           |
| `Financial`  | Monthly financial reports                                 |
| `HOA`        | Board meeting minutes, bylaws, association announcements  |
| `Event`      | Garage sales, community events, etc.                      |
| `Local News` | News stories about Indian Village from local media        |

---

## Markdown Quick Reference

Here's how to format your post content:

| What you want         | What you type                          | What it looks like          |
|----------------------|----------------------------------------|-----------------------------|
| Bold text            | `**bold text**`                        | **bold text**               |
| Italic text          | `*italic text*`                        | *italic text*               |
| Link                 | `[link text](https://example.com)`     | [link text](https://example.com) |
| Heading              | `## Section Title`                     | (large bold heading)        |
| Smaller heading      | `### Subsection`                       | (medium bold heading)       |
| Bulleted list        | `- Item one`                           | - Item one                  |
| Numbered list        | `1. First item`                        | 1. First item               |
| Horizontal line      | `---`                                  | (divider line)              |
| Blockquote           | `> quoted text`                        | > quoted text               |

### Example: Financial Report Post

```
---
title: "Financial Report - March 2026"
date: 2026-04-01T00:00:00-04:00
author: "Monica Hadsall"
categories: ["Financial"]
---

This report contains the full and complete financial information we have
available, collected from bank account balances, all sources of income,
and all expenses for the previous month.

Beginning balance from February: **$943.07**

**Income:**
- Dues received: $40.00

**Expenses:**
- AEP entrance monument lights: -$19.50

**Ending total: $963.57**
```

### Example: Meeting Minutes Post

```
---
title: "Board Meeting Minutes - April 3, 2026"
date: 2026-04-04T00:00:00-04:00
author: "Ken Hull"
categories: ["HOA"]
---

**INDIAN VILLAGE COMMUNITY ASSOCIATION**
**BOARD OF GOVERNORS - REGULAR MEETING MINUTES**

**Date:** April 3, 2026
**Format:** Virtual (Video Conference)
**Presiding:** Paul Forbing, President

## 1. Call to Order

Meeting called to order at 7:00 PM.

## 2. Old Business

Discussion about the entrance wall restoration project...

## 3. Adjournment

Meeting adjourned at 8:15 PM.
```

---

## Troubleshooting

**My post isn't showing up on the site.**
- Make sure the file is in the `content/posts/` folder (not somewhere else)
- Check that the filename ends in `.md`
- Verify the date in the front matter is not in the future
- Wait 1-2 minutes for the build to complete

**I made a mistake in a post.**
- Just edit the file again and save/commit. The site will rebuild automatically.

**I want to remove a post.**
- Delete the file from `content/posts/` on GitHub or locally, then commit and push.

**I need help.**
- Contact Paul at board@indianvillagefw.org

---

## Quick Links

- **Website**: https://indianvillagefw.org
- **GitHub repo**: https://github.com/luapgnibrof/indianvillagefw.org
- **Posts folder** (add/edit here): https://github.com/luapgnibrof/indianvillagefw.org/tree/main/content/posts
- **Build status**: https://github.com/luapgnibrof/indianvillagefw.org/actions
