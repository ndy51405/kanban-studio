import json
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from app.schemas import AIChatResponse, BoardData, Card, ChatMessage, Column

# Load .env from project root if present
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

DEFAULT_MODEL = "gemini-3.5-flash-lite"
FALLBACK_MODEL = "gemini-3.8-flash"

SYSTEM_INSTRUCTION = """
You are the AI Project Manager assistant for Kanban Studio.
You help users manage their Kanban project board.

Rules for response:
1. Always provide a helpful, friendly, and concise message in 'reply'.
2. If the user asks you to modify the board (create, edit, move, delete cards, or rename columns):
   - You MUST return the complete updated board in 'board'.
   - Maintain all unchanged columns, cards, and existing IDs.
   - For any new card, create a unique ID (e.g. 'card-' followed by a number, timestamp, or short slug).
   - Ensure every card has a corresponding entry in 'cards' and its ID is placed in the appropriate column's 'cardIds'.
   - When deleting a card, remove it from 'cards' and remove its ID from all column 'cardIds'.
   - When moving a card, remove its ID from the source column's 'cardIds' and append to the destination column's 'cardIds'.
3. If the user's message is conversational or an informational question (e.g. greetings, questions about existing cards or columns, general advice) where no board changes are requested:
   - You MUST set 'board' to null.
"""


class AICard(BaseModel):
    id: str
    title: str
    details: str = ""


class AIColumn(BaseModel):
    id: str
    title: str
    cardIds: list[str] = Field(default_factory=list)


class AIBoardData(BaseModel):
    columns: list[AIColumn]
    cards: list[AICard]


class AIGeminiResponse(BaseModel):
    reply: str
    board: AIBoardData | None = None


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


def ai_board_to_board_data(ai_board: AIBoardData) -> BoardData:
    return BoardData(
        columns=[
            Column(id=col.id, title=col.title, cardIds=col.cardIds)
            for col in ai_board.columns
        ],
        cards={
            card.id: Card(id=card.id, title=card.title, details=card.details)
            for card in ai_board.cards
        },
    )


def chat_with_kanban(
    message: str,
    history: list[ChatMessage],
    current_board: BoardData,
    client: genai.Client | None = None,
    model: str | None = None,
) -> AIChatResponse:
    cli = client or get_client()
    target_model = model or get_model()

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        response_mime_type="application/json",
        response_schema=AIGeminiResponse,
        temperature=0.2,
    )

    board_summary = json.dumps(
        {
            "columns": [col.model_dump() for col in current_board.columns],
            "cards": list(current_board.cards.values()),
        },
        default=lambda o: o.model_dump(),
    )

    prompt_parts: list[str] = [
        f"Current Kanban Board:\n```json\n{board_summary}\n```\n"
    ]
    if history:
        prompt_parts.append("Conversation History:")
        for msg in history:
            role_label = "User" if msg.role == "user" else "Assistant"
            prompt_parts.append(f"{role_label}: {msg.content}")
        prompt_parts.append("")

    prompt_parts.append(f"User: {message}")
    prompt = "\n".join(prompt_parts)

    def _call(mod: str) -> AIChatResponse:
        resp = cli.models.generate_content(
            model=mod,
            contents=prompt,
            config=config,
        )
        parsed = AIGeminiResponse.model_validate_json(resp.text)
        converted_board = (
            ai_board_to_board_data(parsed.board) if parsed.board is not None else None
        )
        return AIChatResponse(reply=parsed.reply, board=converted_board)

    try:
        return _call(target_model)
    except Exception as exc:
        if model is None and target_model != FALLBACK_MODEL and "503" in str(exc):
            return _call(FALLBACK_MODEL)
        raise
