# Jarvis0 — ChatGPT‑style assistant prototype

This repository contains a minimal prototype for a ChatGPT‑style assistant (backend + simple web UI).

What I added in the initial commit:
- FastAPI backend with a placeholder /generate endpoint (backend/app/main.py)
- A tiny static web UI (backend/static/index.html + backend/static/main.js)
- Dockerfile for the backend
- requirements.txt listing the main Python deps
- MIT LICENSE and README

Notes / next steps
- The /generate endpoint is currently a placeholder and does not load a model. I left comments in backend/app/main.py showing where to load an open LLM (e.g., Mistral/Falcon/Llama-2 via transformers, vLLM, or a hosted API).
- Tell me which model you want to target (or say "recommend"). I will add model-loading code, LoRA fine-tuning scripts, and deployment notes next.

How to run locally (quick):

1) From repository root, install dependencies:

   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

2) Start the server:

   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

3) Open http://localhost:8000/ in a browser and use the demo chat UI.

License: MIT (see LICENSE)
