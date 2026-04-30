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
- `job_dialogue/` — in-development web app. Files:
  - `app.html` — frontend UI only; no LLM logic. Password gate on load; Enter submits, Shift+Enter adds newline. Uses `marked.js` (CDN) to render markdown responses. Talks to the Flask backend at `http://localhost:5000`.
  - `server.py` — Flask backend. Exposes two endpoints:
    - `POST /api/auth` — checks password, returns 200 or 401
    - `POST /api/dialogue` — accepts `{job, password}`, fetches URL content if needed, calls the LLM once per archetype in parallel, returns array of `{name, bg, border, full, summary}`
  - `config.py` — all user-facing config: `MODEL` (LiteLLM model string), `QUESTION` (prompt appended after each archetype description), and `ARCHETYPES` array (name, description, bg, border). Add entries to `ARCHETYPES` to add more archetypes.
  - `config_local.py` — gitignored; contains `API_KEY = "..."` and `PASSWORD = "..."`.
  - `requirements.txt` — Python dependencies. Install into the venv with `pip install -r requirements.txt`.
  - `venv/` — gitignored Python virtual environment.

**LLM provider:** uses [LiteLLM](https://docs.litellm.ai/) so the provider is swappable via `MODEL` in `config.py`. Examples: `"claude-haiku-4-5-20251001"` (Anthropic), `"gemini/gemini-2.5-flash-lite"` (Google), `"gpt-4o"` (OpenAI). The `API_KEY` in `config_local.py` should match whichever provider is selected.

**URL fetching:** if the user pastes a URL, `server.py` uses Playwright (headless Chromium) to fetch and parse the page, bypassing bot-detection. Plain text input is passed straight through.

**Response format:** the LLM is instructed to return its full assessment, then `===SUMMARY===`, then a one-paragraph summary. `server.py` splits on this delimiter and returns both `full` and `summary` fields. The UI shows the summary by default with a "Read more" button that expands to the full response.

**To run locally:**
```bash
source job_dialogue/venv/bin/activate
python job_dialogue/server.py
# then open job_dialogue/app.html in a browser
```
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
