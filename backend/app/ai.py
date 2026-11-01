import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# Load .env from project root if present
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

DEFAULT_MODEL = "gemini-3.5-flash-lite"
FALLBACK_MODEL = "gemini-3.5-flash"


def get_gemini_api_key() -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment or .env file")
    return api_key


def get_model() -> str:
    return os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)


def get_client(api_key: str | None = None) -> genai.Client:
    key = api_key or get_gemini_api_key()
    return genai.Client(api_key=key)


def generate_text(
    prompt: str,
    client: genai.Client | None = None,
    model: str | None = None,
) -> str:
    cli = client or get_client()
    target_model = model or get_model()
    try:
        response = cli.models.generate_content(
            model=target_model,
            contents=prompt,
        )
        return (response.text or "").strip()
    except Exception as exc:
        if model is None and target_model != FALLBACK_MODEL and "503" in str(exc):
            response = cli.models.generate_content(
                model=FALLBACK_MODEL,
                contents=prompt,
            )
            return (response.text or "").strip()
        raise
