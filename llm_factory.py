import time
from typing import Callable, TypeVar
from langchain_google_genai import ChatGoogleGenerativeAI
from config import (
    GEMINI_FALLBACK_MODEL,
    GEMINI_MAX_RETRIES,
    GEMINI_MODEL,
    GEMINI_TEMPERATURE,
)


T = TypeVar("T")
def create_gemini_llm(model_name: str | None = None,) -> ChatGoogleGenerativeAI:
    """
    Create a Gemini chat model.
    If model_name is not supplied, the primary configured
    Gemini model is used.
    """
    return ChatGoogleGenerativeAI(
        model=model_name or GEMINI_MODEL,
        temperature=GEMINI_TEMPERATURE,
        max_retries=GEMINI_MAX_RETRIES,
    )

def get_primary_llm() -> ChatGoogleGenerativeAI:
    return create_gemini_llm(GEMINI_MODEL)

def get_fallback_llm() -> ChatGoogleGenerativeAI:
    return create_gemini_llm(GEMINI_FALLBACK_MODEL)

def is_retryable_error(error: Exception) -> bool:
    """
    Determine whether an error is likely temporary and should
    trigger a retry/fallback.

    Handles common Gemini/API availability failures such as:
    - 429 rate limits
    - 500 server errors
    - 502 gateway errors
    - 503 unavailable
    - 504 timeouts
    - connection/network errors
    """
    error_text = str(error).lower()
    retryable_patterns = [
        "429",
        "500",
        "502",
        "503",
        "504",
        "rate limit",
        "resource exhausted",
        "temporarily unavailable",
        "service unavailable",
        "server error",
        "timeout",
        "timed out",
        "connection",
        "remoteprotocolerror",
        "internal server error",
    ]

    return any(
        pattern in error_text
        for pattern in retryable_patterns
    )

def invoke_with_fallback(
    primary_callable: Callable[[], T],
    fallback_callable: Callable[[], T],
    max_attempts: int = 2,
) -> T:
    """
    Execute the primary LLM with retries.
    If the primary model continues to fail with a retryable
    error, switch to the fallback model and retry it as well.
    """
    last_primary_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            return primary_callable()
        except Exception as exc:
            last_primary_error = exc
            print(
                f"[Primary LLM] Attempt "
                f"{attempt}/{max_attempts} failed: {exc}"
            )

            if not is_retryable_error(exc):
                raise
            if attempt < max_attempts:
                wait_time = 2 ** (attempt - 1)
                print(
                    f"[Primary LLM] Retrying in "
                    f"{wait_time} seconds..."
                )
                time.sleep(wait_time)
    print("\n[LLM FALLBACK] " "Primary model unavailable.")
    print(
        f"[LLM FALLBACK] Switching to: "
        f"{GEMINI_FALLBACK_MODEL}"
    )

    last_fallback_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            return fallback_callable()
        except Exception as exc:
            last_fallback_error = exc
            print(
                f"[LLM FALLBACK] Attempt "
                f"{attempt}/{max_attempts} failed: {exc}"
            )
            if not is_retryable_error(exc):
                raise
            if attempt < max_attempts:
                wait_time = 2 ** (attempt - 1)
                print(
                    f"[LLM FALLBACK] Retrying in "
                    f"{wait_time} seconds..."
                )
                time.sleep(wait_time)
    raise RuntimeError(
        "Both primary and fallback Gemini models failed.\n"
        f"Primary error: {last_primary_error}\n"
        f"Fallback error: {last_fallback_error}"
    )

if __name__ == "__main__":
    print("LLM Factory loaded successfully.")
    print(
        f"Primary model: "
        f"{GEMINI_MODEL}"
    )
    print(
        f"Fallback model: "
        f"{GEMINI_FALLBACK_MODEL}"
    )
    primary = get_primary_llm()
    fallback = get_fallback_llm()
    print(
        f"Primary LLM created: "
        f"{type(primary).__name__}"
    )
    print(
        f"Fallback LLM created: "
        f"{type(fallback).__name__}"
    )