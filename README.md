# Forkcast — Gemini Edition

Forkcast is a Streamlit decision-analysis app. Enter one decision; Google Gemini generates three subject-specific paths, pros/cons, assumptions, alternative futures, and recommendations. Transparent rankings are calculated separately by deterministic Python code.

## Run locally
1. Install Python 3.11 or newer.
2. Open PowerShell in this folder.
3. Run `python -m pip install -r requirements.txt`
4. Run `python -m streamlit run app.py`
5. Open the URL shown in the terminal, usually http://localhost:8501.
6. Expand **Gemini API settings** and paste your key from Google AI Studio. Choose `gemini-2.5-flash` unless your account supports a different model.

## Security and deployment
The key is entered into a password field and held in Streamlit session state; it is not written to source files. Never paste your key into chat, screenshots, source control, or a public repository. For a public deployment, prefer a server-side environment secret and avoid logging request URLs (the Gemini API key is part of the request URL in this simple REST implementation). User decisions/context are sent to Google's Gemini API for generation. Built-in samples work without an API key.

## Troubleshooting
- HTTP 400/403: check key, Gemini API access, model name and quota.
- Connection error: check internet connection.
- Invalid JSON/too few options: retry once; the app expects structured JSON output.

The project uses Python's standard library for Gemini REST calls; no extra Gemini SDK is required.
