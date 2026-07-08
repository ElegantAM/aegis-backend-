
"""
live_aegis_server.py
---------------------
Flask backend that proxies requests to Groq (via the OpenAI-compatible
client), with CORS locked down and traceback logging for debugging on Render.
"""

import os
import traceback
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI, APIError, APIConnectionError, RateLimitError

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("aegis")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

if not GROQ_API_KEY:
    logger.error("FATAL: GROQ_API_KEY environment variable is not set.")

ALLOWED_ORIGINS = [
    "https://elegantam.github.io",
]

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGINS}})

client = None
if GROQ_API_KEY:
    client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

SYSTEM_PROMPT = (
    "You are AEGIS, a preliminary consumer-rights and compliance assessment "
    "assistant for Indian consumers. Given a user's submitted grievance or "
    "case description, produce a clear, structured preliminary assessment: "
    "relevant consumer protection considerations, likely next steps, and any "
    "caveats. Always note this is a preliminary assessment, not formal legal advice."
)


@app.route("/", methods=["GET"])
def root():
    return jsonify({"service": "aegis-proxy", "status": "online"})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok" if GROQ_API_KEY else "degraded",
        "groq_key_configured": bool(GROQ_API_KEY),
        "model": GROQ_MODEL,
    }), 200 if GROQ_API_KEY else 503


@app.route("/", methods=["POST"])
def process_assessment():
    if client is None:
        logger.error("Blocked request: GROQ_API_KEY missing at request time.")
        return jsonify({"error": "Server misconfiguration: GROQ_API_KEY not set."}), 503

    try:
        data = request.get_json(force=True, silent=True)
        if not data or "prompt" not in data:
            return jsonify({"error": "Missing computational payload"}), 400

        user_issue = data["prompt"]
        if not isinstance(user_issue, str) or not user_issue.strip():
            return jsonify({"error": "'prompt' must be a non-empty string"}), 400

        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_issue},
            ],
            temperature=0.3,
            max_tokens=1024,
        )

        result_text = completion.choices[0].message.content

        analysis_report = (
            f"[AEGIS CORE COGNITIVE PIPELINE ENGAGED]\n"
            f"[INPUT BLOCK ISOLATED AND PARSED SUCCESSFULLY]\n\n"
            f"==================================================\n"
            f"          PRELIMINARY RIGHTS ASSESSMENT\n"
            f"==================================================\n"
            f"SUBMITTED CASE DATA:\n\"{user_issue}\"\n\n"
            f"AI ASSESSMENT:\n{result_text}\n\n"
            f"STATUS: Core analysis complete."
        )

        return jsonify({"success": True, "model": GROQ_MODEL, "analysis": analysis_report}), 200

    except RateLimitError as e:
        logger.error("Groq rate limit: %s", e)
        return jsonify({"error": "Upstream rate limit reached. Try again shortly."}), 429

    except APIConnectionError as e:
        logger.error("Groq connection error: %s\n%s", e, traceback.format_exc())
        return jsonify({"error": "Could not reach the AI provider."}), 502

    except APIError as e:
        logger.error("Groq API error: %s\n%s", e, traceback.format_exc())
        return jsonify({"error": "The AI provider returned an error."}), 502

    except Exception as e:
        logger.error("Unhandled exception: %s\n%s", e, traceback.format_exc())
        return jsonify({"error": "Internal server error."}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
