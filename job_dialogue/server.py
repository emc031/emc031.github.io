import asyncio
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

from config import MODEL, QUESTION, ARCHETYPES
try:
    from config_local import API_KEY
except ImportError:
    print("ERROR: config_local.py not found. Create job_dialogue/config_local.py with: API_KEY = \"your-gemini-api-key\"", file=sys.stderr)
    API_KEY = None

app = Flask(__name__)
CORS(app)

if API_KEY:
    genai.configure(api_key=API_KEY)


async def call_archetype(archetype, job):
    model = genai.GenerativeModel(MODEL)
    prompt = archetype["description"] + QUESTION + job
    response = await asyncio.to_thread(model.generate_content, prompt)
    return {
        "name": archetype["name"],
        "bg": archetype["bg"],
        "border": archetype["border"],
        "text": response.text,
    }


@app.post("/api/dialogue")
def dialogue():
    if not API_KEY:
        return jsonify({"error": "API key not configured"}), 500

    job = (request.json or {}).get("job", "").strip()
    if not job:
        return jsonify({"error": "No job description provided"}), 400

    async def run_all():
        return await asyncio.gather(
            *[call_archetype(a, job) for a in ARCHETYPES],
            return_exceptions=True,
        )

    results = asyncio.run(run_all())

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
