import asyncio
import sys
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from flask_cors import CORS
import litellm
from playwright.async_api import async_playwright

import os

from config import MODEL, QUESTION, ARCHETYPES
try:
    from config_local import LLM_API_KEY, WEBSITE_PASSWORD
except ImportError:
    LLM_API_KEY = os.environ.get("LLM_API_KEY")
    WEBSITE_PASSWORD = os.environ.get("WEBSITE_PASSWORD")
    if not LLM_API_KEY:
        print("WARNING: No LLM_API_KEY found in config_local.py or environment.", file=sys.stderr)

app = Flask(__name__)
CORS(app)


async def fetch_url_text(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle", timeout=15000)
        html = await page.content()
        await browser.close()
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return " ".join(soup.get_text(separator=" ").split())


async def resolve_job_text(raw):
    if raw.startswith("http://") or raw.startswith("https://"):
        return await fetch_url_text(raw)
    return raw


async def call_archetype(archetype, job):
    prompt = archetype["description"] + QUESTION + job
    response = await asyncio.to_thread(
        litellm.completion,
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        api_key=LLM_API_KEY,
    )
    raw = response.choices[0].message.content
    parts = raw.split("===SUMMARY===", 1)
    full = parts[0].strip()
    summary = parts[1].strip() if len(parts) == 2 else full

    return {
        "name": archetype["name"],
        "intro": archetype.get("intro", ""),
        "intro_label": archetype.get("intro_label", ""),
        "bg": archetype["bg"],
        "border": archetype["border"],
        "full": full,
        "summary": summary,
    }


@app.post("/api/auth")
def auth():
    body = request.json or {}
    if not app.debug and WEBSITE_PASSWORD and body.get("password") != WEBSITE_PASSWORD:
        return jsonify({"error": "Incorrect password"}), 401
    return jsonify({"ok": True})


@app.post("/api/dialogue")
def dialogue():
    if not LLM_API_KEY:
        return jsonify({"error": "API key not configured"}), 500

    body = request.json or {}

    if WEBSITE_PASSWORD and body.get("password") != WEBSITE_PASSWORD:
        return jsonify({"error": "Incorrect password"}), 401

    job_raw = body.get("job", "").strip()
    if not job_raw:
        return jsonify({"error": "No job description provided"}), 400

    async def run_all():
        job = await resolve_job_text(job_raw)
        return await asyncio.gather(
            *[call_archetype(a, job) for a in ARCHETYPES],
            return_exceptions=True,
        )

    try:
        results = asyncio.run(run_all())
    except Exception as e:
        return jsonify({"error": f"Could not fetch URL: {e}"}), 400

    responses = []
    for archetype, result in zip(ARCHETYPES, results):
        if isinstance(result, Exception):
            responses.append({
                "name": archetype["name"],
                "intro": archetype.get("intro", ""),
        "intro_label": archetype.get("intro_label", ""),
                "bg": archetype["bg"],
                "border": archetype["border"],
                "error": str(result),
            })
        else:
            responses.append(result)

    return jsonify(responses)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
