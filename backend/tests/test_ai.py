import os
from unittest.mock import MagicMock
import pytest

from app.ai import (
    DEFAULT_MODEL,
    generate_text,
    get_gemini_api_key,
    get_model,
)


def test_get_model_default() -> None:
    original = os.environ.get("GEMINI_MODEL")
    try:
        os.environ.pop("GEMINI_MODEL", None)
        assert get_model() == DEFAULT_MODEL
    finally:
        if original is not None:
            os.environ["GEMINI_MODEL"] = original


def test_get_model_custom(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_MODEL", "custom-model")
    assert get_model() == "custom-model"


def test_get_gemini_api_key_missing_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="GEMINI_API_KEY is not set"):
        get_gemini_api_key()


def test_generate_text_mock_client() -> None:
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Mocked AI Response"
    mock_client.models.generate_content.return_value = mock_response

    result = generate_text("Hello Gemini", client=mock_client, model="test-model")
    assert result == "Mocked AI Response"
    mock_client.models.generate_content.assert_called_once_with(
        model="test-model",
        contents="Hello Gemini",
    )


def test_live_gemini_connectivity() -> None:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not found in environment; skipping live test")

    result = generate_text("What is 2+2? Reply with just the number.")
    assert "4" in result

