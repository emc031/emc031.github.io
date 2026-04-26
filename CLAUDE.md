# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A static website for [Integral Altruism](https://integralaltruism.com), hosted on GitHub Pages (`emc031.github.io`) with a custom domain set via `CNAME`. No build step, no framework, no dependencies — everything is plain HTML/CSS.

## Development

Open `index.html` directly in a browser, or serve it locally:

```bash
python3 -m http.server 8080
# then visit http://localhost:8080
```

Deploy by pushing to `main`; GitHub Pages publishes automatically.

## Structure

- `index.html` — the entire site: inline CSS, content, and a small JS snippet for the mobile hamburger menu
- `inta.svg` — logo used in the nav and as a faint hero background watermark
- `inta_retreat.png` — retreat photo in the "in practice" section
- `job_dialogue/` — in-development web app (served at `/job_dialogue/app.html`). Files:
  - `app.html` — UI and Gemini API call logic. Enter submits, Shift+Enter adds newline.
  - `config.js` — all user-facing config: `MODEL`, `QUESTION`, and `ARCHETYPES` array (name, description, bg, border). Add entries to `ARCHETYPES` to add more archetypes.
  - `config.local.js` — gitignored; contains `const API_KEY = "..."` with the Gemini key. Page shows an error and disables the button if this file is missing or key is unset.
- `CNAME` — sets custom domain to `integralaltruism.com`

## Design tokens (CSS variables in `index.html`)

| Variable | Value | Use |
|---|---|---|
| `--bg` | `#f5f2ed` | page background |
| `--ink` | `#1a1a18` | body text |
| `--ink-muted` | `#5a5750` | secondary text, labels |
| `--accent` | `#b5451b` | links, borders, CTA buttons |
| `--accent-light` | `#f5e0d8` | callout background, hover |
| `--border` | `#ddd9d2` | section dividers |
| `--max-w` | `720px` | content column width |

Fonts are loaded from Google Fonts: **Lora** (headings, logo, italic accents) and **DM Sans** (body).

## Content sections

The page has three `<section>` blocks identified by `id`: `#theory`, `#practice`, and `#reading`. The reading section uses a CSS grid (`reading-grid`) with columns keyed by topic (Rationality, AI, EA & Cause Prioritisation).

External links (events, substack, YouTube, donate, get-involved form) are plain `<a target="_blank">` tags — update them directly in `index.html` when URLs change.
