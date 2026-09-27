import os
from typing import Optional

from dotenv import load_dotenv
from groq import Groq


# Load variables from a local .env file if present.
load_dotenv()

_client: Optional[Groq] = None


def get_groq_client() -> Groq:
    """Configure and return a singleton Groq client using environment vars."""

    global _client

    if _client is not None:
        return _client

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY environment variable is not set")

    _client = Groq(api_key=api_key)
    return _client


def call_llm(
    system_prompt: str,
    user_message: str,
    model: Optional[str] = None,
    max_tokens: int = 500,
) -> str:
    """Call the LLM with a system prompt and user message and return text."""

    client = get_groq_client()

    raw_model = model or os.getenv("GROQ_MODEL") or "qwen/qwen3.8-27b"
    # Auto-sanitize deprecated or problematic model names
    if raw_model in {"llama-3.1-8b-instant", "llama3-8b-8192", "groq/compound-mini", "groq/compound"}:
        model_name = "qwen/qwen3.8-27b"
    else:
        model_name = raw_model

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.0,
            max_tokens=max_tokens,
        )
        content = response.choices[0].message.content
        return content or ""
    except Exception as e:
        # Fallback to qwen/qwen3.8-27b if the requested model failed
        if model_name != "qwen/qwen3.8-27b":
            response = client.chat.completions.create(
                model="qwen/qwen3.8-27b",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.0,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            return content or ""
        raise e