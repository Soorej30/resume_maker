import os
from typing import Any


def _get_client() -> Any:
    from groq import Groq

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Export it before running the resume pipeline."
        )
    return Groq(api_key=api_key)


def call_llm(prompt: str, model: str = "llama-3.3-70b-versatile", temperature: float = 0.3) -> str:
    client = _get_client()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("LLM returned an empty response.")
    content = content.strip()
    if not content:
        raise RuntimeError("LLM returned only whitespace.")
    return content
