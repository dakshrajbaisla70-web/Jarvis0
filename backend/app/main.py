from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Jarvis0 - Prototype")

# Allow CORS for local testing — adjust in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "../static")
INDEX_HTML = os.path.join(STATIC_DIR, "index.html")


@app.get("/", response_class=FileResponse)
async def index():
    """Serve the demo chat UI."""
    return FileResponse(INDEX_HTML)


@app.post("/generate")
async def generate(request: Request):
    """Generate a reply for a user message.

    This endpoint is a placeholder. It echoes back the message and includes a
    static note. Replace the body with model loading + inference code when you
    pick a target model.
    """
    data = await request.json()
    message = data.get("message", "")

    # Placeholder reply — replace with actual model inference
    reply = {
        "reply": f"[Placeholder reply] I received: {message}",
        "note": "This is a placeholder. Ask me to load a model (e.g., Mistral-7B) and I'll add real inference code.",
    }
    return JSONResponse(content=reply)
