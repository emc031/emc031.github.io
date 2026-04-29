import asyncio
import sys
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from flask_cors import CORS
import litellm
from playwright.async_api import async_playwright

from config import MODEL, QUESTION, ARCHETYPES
try:
    from config_local import API_KEY, PASSWORD
except ImportError:
    print("ERROR: config_local.py not found. Create job_dialogue/config_local.py with API_KEY and PASSWORD.", file=sys.stderr)
    API_KEY = None
    PASSWORD = None

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
        api_key=API_KEY,
    )
    return {
        "name": archetype["name"],
        "bg": archetype["bg"],
        "border": archetype["border"],
        "text": response.choices[0].message.content,
    }


@app.post("/api/auth")
def auth():
    body = request.json or {}
    if PASSWORD and body.get("password") != PASSWORD:
        return jsonify({"error": "Incorrect password"}), 401
    return jsonify({"ok": True})


@app.post("/api/dialogue")
def dialogue():
    if not API_KEY:
        return jsonify({"error": "API key not configured"}), 500

    body = request.json or {}

    if PASSWORD and body.get("password") != PASSWORD:
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
                "bg": archetype["bg"],
                "border": archetype["border"],
                "error": str(result),
            })
        else:
            responses.append(result)

    return jsonify(responses)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
